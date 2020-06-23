from selenium import webdriver
from flask import Flask, render_template, session, request, copy_current_request_context
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from threading import Lock
import time
import re


def get_result():
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument("--headless")
    print(options)

    browser = webdriver.Chrome(executable_path="chromedriver", options=options)
    browser.get('https://192.168.0.110:8443/#/login/?referrer=%2Fapp%2Feu.saimos.edge.count%2Fstats')
    loginElement = browser.find_element_by_xpath("//input[@aria-label='Username']")
    loginElement.send_keys('admin')
    passwordElement = browser.find_element_by_xpath("//input[@aria-label='Password']")
    passwordElement.send_keys('admin')

    loginButton = browser.find_element_by_class_name("v-btn__content")
    loginButton.click()
    try:
        time.sleep(3)
        entry = browser.find_element_by_class_name("enter").text
        entry = int(re.search(r'\d+', entry).group())
        leave = browser.find_element_by_class_name("leave").text
        leave = int(re.search(r'\d+', leave).group())
    except:
        entry = 0
        leave = 0
    finally:
        browser.quit()
    browser.quit()
    return entry-leave


async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///occupancy.sqlite3'
thread = None
thread_lock = Lock()

db = SQLAlchemy(app)



class Occupancy(db.Model):
    id = db.Column('bucket_id', db.Integer, primary_key=True)
    bucket = db.Column(db.String(100))
    value = db.Column(db.String(50))
    # rezolucija je 60 min


def background_thread():
    """Example of how to send server generated events to clients."""
    while True:
        socketio.sleep(3)
        count = get_result()
        time.sleep(5)
        socketio.emit('my_response',
                      {'count': count},
                      namespace='/test')
        print("Emitovano: ",count)


@app.route("/")
def home():

    podaci = {}
    return render_template("index.html", async_mode=socketio.async_mode)


@socketio.on('my event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']})


@socketio.on('my broadcast event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']}, broadcast=True)


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == "__main__":
    socketio.run(debug=True)
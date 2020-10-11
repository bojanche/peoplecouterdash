from selenium import webdriver
from flask import Flask, render_template, session, request, copy_current_request_context
from flask_socketio import SocketIO, emit
# from flask_sqlalchemy import SQLAlchemy
from threading import Lock
import time
import re
from datetime import datetime


adresa = "192.168.2.112"
offset = 0


def get_result(adres):
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-proxy-server")
    # print("1. Vreme pocetka poziva chromiuma: ", datetime.now())

    browser = webdriver.Chrome(executable_path="chromedriver.exe", options=options, service_args=["--verbose", "--log-path=chromedirver.log"])
    browser.get('https://'+adres+':8443/#/login/?referrer=https%3A%2F%2F192.168.2.112%3A8443%2Fapp%2Feu.saimos.edge.count%2Fstats')
    # print("2. Vreme pocetka koriscenja chromiuma: ", datetime.now())
    # loginElement = browser.find_element_by_xpath("//input[@aria-label='Username']")
    loginElement = browser.find_element_by_id("Login_username")
    loginElement.send_keys('bojan')
    # passwordElement = browser.find_element_by_xpath("//input[@aria-label='Password']")
    passwordElement = browser.find_element_by_id("Login_password")
    passwordElement.send_keys('Bojana2512')

    loginButton = browser.find_element_by_class_name("v-btn__content")
    loginButton.click()
    # print("3. Chromium se ulogovao: ", datetime.now())
    try:
        # print("4. Vreme pocetka trazenja elemenata: ", datetime.now())
        entry = browser.find_element_by_class_name("enter").text
        entry = int(re.search(r'\d+', entry).group())
        # print("5. Nasao enter: ", datetime.now())
        leave = browser.find_element_by_class_name("leave").text
        leave = int(re.search(r'\d+', leave).group())
        # print("6. Nasao leave: ", datetime.now())
    except:
        entry = 0
        leave = 0
    finally:
        print("7. Probam browser izlaz: ", datetime.now())
        browser.quit()
    # print("8. Izasao i pucam rezultat: ", datetime.now(), entry-leave)
    return entry-leave+offset


async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///occupancy.sqlite3'
thread = None
thread_lock = Lock()

# db = SQLAlchemy(app)


# class Occupancy(db.Model):
#     id = db.Column('bucket_id', db.Integer, primary_key=True)
#     bucket = db.Column(db.String(100))
#     value = db.Column(db.String(50))
#     # rezolucija je 60 min
#
#
# class Setup(db.Model):
#     camera_ip = db.Column(db.String(50))
#     startup_value = db.Column(db.String(50))


def background_thread():
    """Example of how to send server generated events to clients."""
    while True:
        socketio.sleep(3)
        count = get_result(adresa)
        time.sleep(5)
        socketio.emit('my_response',
                      {'count': count},
                      namespace='/test')
        print("Emitovano: ",count)


@app.route("/")
def home():
    return render_template("index.html", async_mode=socketio.async_mode)


@app.route("/settings")
def settings():
    return render_template("settings.html")


@socketio.on('my broadcast event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']}, broadcast=True)


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    print("Connected ")
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


@socketio.on('message', namespace='/test')
def handle_message(message):
    global offset
    if message['data'] == 1:
        offset = offset + 1
    else:
        offset = offset - 1
    print('Current offset: ', offset)


if __name__ == "__main__":
    socketio.run(debug=True)
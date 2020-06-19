# import requests
#
# # Fill in your details here to be posted to the login form.
# payload = {
#     'Username': 'admin',
#     'Password': 'admin'
# }
#
# # Use 'with' to ensure the session context is closed after use.
# with requests.Session() as s:
#     p = s.post("https://192.168.39.102:8443#/login/?referrer=/app/eu.saimos.edge.count/stats", data=payload, verify=False)
#     # print the html returned or something more intelligent to see if it's a successful login page.
#     print(p.text)

    # # An authorised request.
    # r = s.get('https://192.168.39.102:8443#/login/?referrer=/app/com.securityandsafetythings.webui/')
    # print(r.text)

from selenium import webdriver

capabilities = webdriver.DesiredCapabilities().FIREFOX
capabilities['acceptSslCerts']=True

browser = webdriver.Firefox(capabilities=capabilities)
browser.get('https://192.168.39.102:8443/#/login/?referrer=%2Fapp%2Feu.saimos.edge.count%2Fstats')
loginElement = browser.find_element_by_xpath("//input[@aria-label='Username']")
loginElement.send_keys('admin')
passwordElement = browser.find_element_by_xpath("//input[@aria-label='Password']")
passwordElement.send_keys('admin')


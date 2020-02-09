from selenium import webdriver
import paho.mqtt.publish as publish
from pyvirtualdisplay import Display

display = Display(visible=0, size=(800, 600))
display.start()

browser = webdriver.Chrome()

browser.set_window_size(1440, 900)

browser.get("https://app.smartoilgauge.com/app.php")
browser.find_element_by_id("inputUsername").send_keys("YOUR_SMART_OIL_USERNAME")
browser.find_element_by_id("inputPassword").send_keys("YOUR_SMART_OIL_PASSWORD")
browser.find_element_by_css_selector("button.btn").click()
browser.implicitly_wait(3)

nav = browser.find_element_by_xpath('//p[contains(text(), "/")]').text
nav_value = nav.split(r"/")
browser.quit()
print(nav_value[0])
publish.single("oilgauge/tanklevel", nav_value[0], hostname="YOUR_MQTT_SERVER", port=1883, auth={'username':"YOUR_MQTT_USER", 'password':"YOUR_MQTT_PASSWORD"})

display.stop()
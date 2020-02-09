# Smart Oil Gauge in Home Assistant
Web scraper for the Smart Oil Gauge to bring data into Home Assistant. This simple solution scrapes the Smart Oil Gauge website and sends a captured value via mqtt to a Home Assistant sensor. I run this on an Ubuntu server using cron to call the script each hour.

### Dependencies
1. Home Assistant
2. mqtt server on Home Assistant
3. Python
4. Smart Oil Gauge sensor

#### Python Code

```python
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
```

#### Home Assistant sensor

```
- platform: mqtt
  state_topic: "oilgauge/tanklevel"
  unit_of_measurement: "gallons"
  name: "Oil level"
```

#### Crontab

Call the script in your Crontab (this is for each hour)
```
0 * * * *  python /path/to/oil.py
```

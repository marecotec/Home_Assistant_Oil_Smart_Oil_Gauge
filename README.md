# Smart Oil Gauge in Home Assistant
Web scraper for the Smart Oil Gauge to bring data into Home Assistant. This simple solution scrapes the Smart Oil Gauge website and sends a captured value via mqtt to a Home Assistant sensor. I run this on an Ubuntu server using cron to call the script each hour.

### Dependencies
1. Home Assistant
2. mqtt server on Home Assistant
3. Python (and a couple of packages)
4. Smart Oil Gauge sensor

#### Python Code - Single message

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

#### Home Assistant sensor - Single message

```
- platform: mqtt
  state_topic: "oilgauge/tanklevel"
  unit_of_measurement: "gallons"
  name: "Oil level"
```

#### Python Code - Multiple message
```python
from selenium import webdriver
import paho.mqtt.publish as publish
import json
from pyvirtualdisplay import Display

display = Display(visible=0, size=(800, 600))
display.start()

browser = webdriver.Chrome()

browser.set_window_size(1440, 900)

user_name = "YOUR_SMART_OIL_USERNAME"
password = "YOUR_SMART_OIL_PASSWORD"
mqtt_server = "YOUR_MQTT_SERVER"
mqtt_user = "YOUR_MQTT_USER"
mqtt_password = "YOUR_MQTT_PASSWORD"


browser.get("https://app.smartoilgauge.com/app.php")
browser.find_element_by_id("inputUsername").send_keys(user_name)
browser.find_element_by_id("inputPassword").send_keys(password)
browser.find_element_by_css_selector("button.btn").click()
browser.implicitly_wait(3)

var = browser.find_element_by_xpath('//p[contains(text(), "/")]').text
fill_level = browser.find_element_by_xpath("//div[@class='ts_col ts_level']//div[@class='ts_col_val']//p").get_attribute("innerHTML")
fill_level = fill_level.split(r"/")
current_fill_level = fill_level[0]
current_fill_proportion = round((float(str(fill_level[0])) / float(str(fill_level[1]))) * 100, 1)
battery_status = browser.find_element_by_xpath("//div[@class='ts_col ts_battery']//div[@class='ts_col_val']//p").get_attribute("innerHTML")
days_to_low = browser.find_element_by_xpath("//div[@class='ts_col ts_days_to_low']//div[@class='ts_col_val']//p").get_attribute("innerHTML")

print(current_fill_level)
print(current_fill_proportion)
print(battery_status)
print(days_to_low)

msgs = [{"topic": "oilgauge/tanklevel", "payload": json.dumps({"current_fill_level": current_fill_level,
                                                               "current_fill_proportion": current_fill_proportion,
                                                               "battery_status": battery_status,
                                                               "days_to_low": days_to_low }) }]
browser.quit()
publish.multiple(msgs, hostname=mqtt_server, port=1883, auth={'username':mqtt_user, 'password':mqtt_password})
```


#### Home Assistant sensors - Multiple message

```
- platform: mqtt
  state_topic: "oilgauge/tanklevel"
  value_template: '{{value_json.current_fill_level}}'
  unit_of_measurement: "gallons"
  name: "Oil level"
- platform: mqtt
  state_topic: "oilgauge/tanklevel"
  value_template: '{{value_json.current_fill_proportion}}'
  unit_of_measurement: "%"
  name: "Oil level percent"
- platform: mqtt
  state_topic: "oilgauge/tanklevel"
  value_template: '{{value_json.battery_status}}'
  name: "Oil level battery"
- platform: mqtt
  state_topic: "oilgauge/tanklevel"
  value_template: '{{value_json.days_to_low}}'
  unit_of_measurement: "days"
  name: "Oil level days to low"
```

#### Crontab

Call the script in your Crontab (this is for each hour)
```
0 * * * *  python /path/to/oil.py
```

or

```
0 * * * *  python /path/to/oil_multiple.py
```

"""
Parse prices of an item from amazon.

custom_component by Mike Auer
"""
import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_time_interval
from homeassistant.const import (CONF_NAME, CONF_ALIAS, CONF_ZONE)

REQUIREMENTS = ['']
_LOGGER = logging.getLogger(__name__)
DEFAULT_NAME = 'Amazon Price'
CONF_ITEMS = 'items'
ICON = 'mdi:coin'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
      vol.Required(CONF_NAME): cv.string,
      vol.Exclusive(CONF_ALIAS, 'XOR'): cv.string,
      vol.Required(CONF_ZONE): cv.string,
    }), cv.has_at_least_one_key(CONF_ALIAS)
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Amazon sensor."""
from lxml import html  
import csv,os,json
import requests
from time import sleep
 
def AmzonParser(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    page = requests.get(url,headers=headers)
    while True:
        sleep(3)
        try:
            doc = html.fromstring(page.content)
            XPATH_NAME = '//h1[@id="title"]//text()'
            XPATH_SALE_PRICE = '//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()'
            XPATH_ORIGINAL_PRICE = '//td[contains(text(),"List Price") or contains(text(),"M.R.P") or contains(text(),"Price")]/following-sibling::td/text()'
            XPATH_CATEGORY = '//a[@class="a-link-normal a-color-tertiary"]//text()'
            XPATH_AVAILABILITY = '//div[@id="availability"]//text()'
 
            NAME = ' '.join(''.join(doc.xpath(XPATH_NAME)).split()) if doc.xpath(XPATH_NAME) else None
            SALE_PRICE = ' '.join(''.join(doc.xpath(XPATH_SALE_PRICE)).split()).strip() if doc.xpath(XPATH_SALE_PRICE) else None
            CATEGORY = ' > '.join([i.strip() for i in doc.xpath(XPATH_CATEGORY)]) if doc.xpath(XPATH_CATEGORY) else None
            ORIGINAL_PRICE = ''.join(doc.xpath(XPATH_ORIGINAL_PRICE)).strip() if doc.xpath(XPATH_ORIGINAL_PRICE) else None
            AVAILABILITY = ''.join(doc.xpath(XPATH_AVAILABILITY)).strip() if doc.xpath(XPATH_AVAILABILITY) else None
 
            if not ORIGINAL_PRICE:
                ORIGINAL_PRICE = SALE_PRICE
 
            if page.status_code!=200:
                raise ValueError('captha')
            data = {
                    'NAME':NAME,
                    'SALE_PRICE':SALE_PRICE,
                    'CATEGORY':CATEGORY,
                    'ORIGINAL_PRICE':ORIGINAL_PRICE,
                    'AVAILABILITY':AVAILABILITY,
                    'URL':url,
                    }
 
            return data
        except Exception as e:
            print(e)
 
def ReadAsin():
    # AsinList = csv.DictReader(open(os.path.join(os.path.dirname(__file__),"Asinfeed.csv")))
    AsinList = ['B0749ZSPP6',
    'B01J2BL01K',
    'B01KGEW44Y',
    'B0777MMZZH',
    'B01K9MR3LC',
    'B075LKCLVP',]
    extracted_data = []
    for i in AsinList:
        url = "https://www.amazon.de/dp/"+i
        print("Processing: "+url)
        extracted_data.append(AmzonParser(url))
        sleep(5)
    f=open('data.json','w')
    json.dump(extracted_data,f,indent=4)
 
 
if __name__ == "__main__":
    ReadAsin()

    add_devices([AmazonSensor()])


class AmazonSensor(Entity):
    """Implementation of the sensor."""

    def __init__(self):
        """Initialize the sensor."""
      self._state = None

#        self._name = item.get(CONF_NAME)
#        self._item = self._parser.load(item.get(CONF_ALIAS),
#                                       item.get(CONF_ZONE))
#        if self._item is None:
#            raise ValueError("id and url could not be resolved")

    @property
    def name(self):
        """Return the name of the item."""
        return 'Example Temerature'
#        return self._name if self._name is not None else self._item.NAME

    @property
    def icon(self):
        """Return the icon for the frontend."""
        return ICON

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = 23
        
#    @property
#    def state(self):
#        """Return the price of the selected product."""
#        return self._item.ORIGINAL_PRICE

#    @property
#    def entity_picture(self):
#        """Return the image."""
#        return self._item.image

#    @property
#    def device_state_attributes(self):
#        """Return the state attributes."""
#        attrs = {'name': self._item.NAME,
#                 'availablilty': self._item.AVAILABILITY,
#                 'original price': self._item.ORIGINAL_PRICE,
#                 'sale price': self._item.SALE_PRICE}
#        return attrs

#    @Throttle(MIN_TIME_BETWEEN_UPDATES)
#    def update(self):
#        """Get the latest price from gearbest and updates the state."""
#        self._item.update()


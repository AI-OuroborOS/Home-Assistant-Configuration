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

CONF_ITEMS = 'items'

ICON = 'mdi:coin'
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=2*60*60)  # 2h
MIN_TIME_BETWEEN_CURRENCY_UPDATES = timedelta(seconds=12*60*60)  # 12h


_ITEM_SCHEMA = vol.All(
    vol.Schema({
        vol.Exclusive(CONF_ALIAS, 'XOR'): cv.string,
        vol.Exclusive(CONF_ZONE, 'XOR'): cv.string,
        vol.Optional(CONF_NAME): cv.string,
    }))

_ITEMS_SCHEMA = vol.Schema([_ITEM_SCHEMA])

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ITEMS): _ITEMS_SCHEMA
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Amazon sensor."""
from lxml import html  
import csv,os,json
import requests
from time import sleep

    sensors = []
    items = config.get(CONF_ITEMS)

def ReadAsin():
    # AsinList = csv.DictReader(open(os.path.join(os.path.dirname(__file__),"Asinfeed.csv")))
    AsinList = ['B0046UR4F4',
    'B00JGTVU5A',
    'B00GJYCIVK',]
    extracted_data = []
    for i in AsinList:
        url = "http://www.amazon.com/dp/"+i
        print "Processing: "+url
        extracted_data.append(AmzonParser(url))
        sleep(5)
    f=open('data.json','w')
    json.dump(extracted_data,f,indent=4)
 
def AmzonParser(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.$
    page = requests.get(url,headers=headers)
    while True:
        sleep(3)
        try:
            doc = html.fromstring(page.content)
            XPATH_NAME = '//h1[@id="title"]//text()'
            XPATH_SALE_PRICE = '//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()'
            XPATH_ORIGINAL_PRICE = '//td[contains(text(),"List Price") or contains(text(),"M.R.P") or contains(text(),$
            XPATH_CATEGORY = '//a[@class="a-link-normal a-color-tertiary"]//text()'
            XPATH_AVAILABILITY = '//div[@id="availability"]//text()'
 
            RAW_NAME = doc.xpath(XPATH_NAME)
            RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
            RAW_CATEGORY = doc.xpath(XPATH_CATEGORY)
            RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)
            RAw_AVAILABILITY = doc.xpath(XPATH_AVAILABILITY)
 
            NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
            SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
            CATEGORY = ' > '.join([i.strip() for i in RAW_CATEGORY]) if RAW_CATEGORY else None
            ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else None
            AVAILABILITY = ''.join(RAw_AVAILABILITY).strip() if RAw_AVAILABILITY else None

    for item in items:
        try:
            sensors.append(NAME, SALE_PRICE, CATEGORY, ORIGINAL_PRICE, AVAILABILITY)


            if not ORIGINAL_PRICE:
                ORIGINAL_PRICE = SALE_PRICE
            if page.status_code!=200:
                raise ValueError('captha')
        except Exception as e:
            print(e)


        except ValueError as exc:
            _LOGGER.error(exc)

    add_devices(sensors, True)


class GearbestSensor(Entity):
    """Implementation of the sensor."""

    def __init__(self, item):
        """Initialize the sensor."""
        self._name = item.get(CONF_NAME)
        self._item = self._parser.load(item.get(CONF_ALIAS),
                                       item.get(CONF_ZONE))
        if self._item is None:
            raise ValueError("id and url could not be resolved")

    @property
    def name(self):
        """Return the name of the item."""
        return self._name if self._name is not None else self._item.NAME

    @property
    def icon(self):
        """Return the icon for the frontend."""
        return ICON

    @property
    def state(self):
        """Return the price of the selected product."""
        return self._item.ORIGINAL_PRICE

#    @property
#    def entity_picture(self):
#        """Return the image."""
#        return self._item.image

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {'name': self._item.NAME,
                 'availablilty': self._item.AVAILABILITY,
                 'original price': self._item.ORIGINAL_PRICE,
                 'sale price': self._item.SALE_PRICE}
        return attrs

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest price from gearbest and updates the state."""
        self._item.update()


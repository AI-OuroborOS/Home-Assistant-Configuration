"""
Parse prices of an item from amazon.

custom_component by Mike Auer
"""
import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
import homeassistant.util.dt as dt_util

REQUIREMENTS = ['']
_LOGGER = logging.getLogger(__name__)
DEFAULT_NAME = 'Amazon Price'
CONF_COUNTRY = 'language'
CONF_ASIN = 'asin'

ICON = 'mdi:coin'

SCAN_INTERVAL = timedelta(minutes=240)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
      vol.Required(CONF_COUNTRY): cv.string,
      vol.Required(CONF_ASIN): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Amazon sensor."""
    country = config.get(CONF_COUNTRY)
    asin = config.get(CONF_ASIN)

    add_devices([AmazonSensor(country, asin)], True)


class AmazonSensor(Entity):
    """Implementation of the sensor."""

    def __init__(self, country, asin):
        """Initialize the sensor."""
      self._name = DEFAULT_NAME
      self.data = AmazonPriceParser(country, asin)
      self._state = None

    @property
    def name(self):
        """Return the name of the item."""
        return self._name

    @property
    def icon(self):
        """Return the icon for the frontend."""
        return ICON

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self.data.update()
        
class AmazonPriceParser(object):

    def __init__(self, country, asin):
        from lxml import html
        import csv,os,json
        import requests
        from time import sleep

        self.country = country
        self.asin = asin
        self.products = [{}]
        
        def ReadAsin():
    # AsinList = csv.DictReader(open(os.path.join(os.path.dirname(__file__),"Asinfeed.csv")))
    AsinList = self.asin
    extracted_data = []
    for i in AsinList:
        url = "https://www.amazon.de/dp/"+i
        extracted_data.append(AmzonParser(url))
        sleep(3)
    self.products = data



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
 

 
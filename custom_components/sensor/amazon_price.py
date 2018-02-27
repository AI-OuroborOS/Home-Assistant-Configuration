"""
Parse prices of an item from amazon.

custom_component by Mike Auer
"""
from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
import homeassistant.util.dt as dt_util

REQUIREMENTS = ['lxml==4.1.1','requests==3.0']

_LOGGER = logging.getLogger(__name__)

CONF_ITEMS = 'items'
CONF_ASIN = "asin"
CONF_LANGUAGE = 'language'

ICON = 'mdi:coim'

SCAN_INTERVAL = timedelta(minutes=60)

_ITEM_SCHEMA = vol.All(
    vol.Schema({
        vol.Required(CONF_LANGUAGE): cv.string,
        vol.Required(CONF_ASIN): cv.string,
    })
)

_ITEMS_SCHEMA = vol.Schema([_ITEM_SCHEMA])

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ITEMS): _ITEMS_SCHEMA
    })

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Amazon Price Sensor."""
    items = config.get(CONF_ITEMS)
    language = config.get(CONF_LANGUAGE)
    sensors = []

    for item in items:
        try:
            sensors.append(AmazonPriceSensor(item))
        except ValueError as exc:
            _LOGGER.error(exc)

    add_devices(sensors, True)

class AmazonPriceSensor(Entity):
    """Implementation of a Amazon Price sensor."""

    def __init__(self, item):
        """Initialize the sensor."""
        from lxml import html  
        import requests

        url = "https://www.amazon."+item.get(CONF_LANGUAGE)+"/dp/"+item.get(CONF_ASIN)+"/"
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
        page = requests.get(url,headers=headers)
        try:
            #Get all the Data from Amazon
            doc = html.fromstring(page.content)
            RAW_NAME = doc.xpath('//h1[@id="title"]//text()')
            RAW_SALE_PRICE = doc.xpath('//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()')
            RAW_CATEGORY = doc.xpath('//a[@class="a-link-normal a-color-tertiary"]//text()')
            RAW_ORIGINAL_PRICE = doc.xpath('//td[contains(text(),"List Price") or contains(text(),"M.R.P") or contains(text(),"Price")]/following-sibling::td/text()')
            RAw_AVAILABILITY = doc.xpath('//div[@id="availability"]//text()')

            #Parse everthing together
            NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
            SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
            CATEGORY = ' > '.join([i.strip() for i in RAW_CATEGORY]) if RAW_CATEGORY else None
            ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else None
            AVAILABILITY = ''.join(RAw_AVAILABILITY).strip() if RAw_AVAILABILITY else None

            #Get the Product Image for the Icon
            #RAW_IMAGE = doc.xpath('//div[@id="HLCXComparisonWidget_feature_div"]//img[@alt="'+NAME+'"]/@src')

            #IMAGE = ' '.join(''.join(RAW_IMAGE).split()) if RAW_IMAGE else None

            if not ORIGINAL_PRICE:
                ORIGINAL_PRICE = SALE_PRICE

            if page.status_code!=200:
                raise ValueError('The requested item page returned: HTTP'+page.status_code+'please check asin and language')

            #Write into variables
            self._item = [NAME, SALE_PRICE, CATEGORY, ORIGINAL_PRICE, AVAILABILITY]

            if self._item is None:
                raise ValueError("id and url could not be resolved")

        except Exception as e:
            raise ValueError(e)


    @property
    def name(self):
        """Return the name of the sensor."""
        return self._item[0]

    @property
    def icon(self):
        """Return the icon for the frontend."""
        return ICON

    @property
    def state(self):
        """Return the departure time of the next train."""
        return self._item[1]

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._item[1]

    def update(self):
        """Get the latest delay from bahn.de and updates the state."""
	for item in items:
            try:
            sensors.append(AmazonPriceSensor(item))
            except ValueError as exc:
            _LOGGER.error(exc)

        self.state = self._item[1]

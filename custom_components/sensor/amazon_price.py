"""
Parse prices of an item from amazon.

custom_component by Mike Auer-Peckelsen
https://github.com/reua
"""
import logging
import voluptuous as vol
from datetime import timedelta
from homeassistant.util import Throttle

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
import homeassistant.util.dt as dt_util
from homeassistant.const import (CONF_NAME)

REQUIREMENTS = ['lxml==4.1.1','requests==3.0']

_LOGGER = logging.getLogger(__name__)

CONF_ITEMS = 'items'
CONF_ASIN = "asin"
CONF_DOMAIN = 'domain_ending'

ICON = 'mdi:amazon'

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=2*60*60)

_ITEM_SCHEMA = vol.All(
    vol.Schema({
        vol.Required(CONF_ASIN): cv.string,
        vol.Optional(CONF_DOMAIN): cv.string,
        vol.Optional(CONF_NAME): cv.string
    })
)

_ITEMS_SCHEMA = vol.Schema([_ITEM_SCHEMA])

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ITEMS): _ITEMS_SCHEMA,
    vol.Required(CONF_DOMAIN): cv.string
    })

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Initiate the Amazon Price Sensor/s."""
    domain = config.get(CONF_DOMAIN)
    items = config.get(CONF_ITEMS)
    language = config.get(CONF_DOMAIN)
    sensors = []

    for item in items:
        try:
            sensors.append(AmazonPriceSensor(item, domain))
        except ValueError as exc:
            _LOGGER.error(exc)

    add_devices(sensors, True)

class AmazonPriceSensor(Entity):
    """Implementation of a Amazon Price sensor."""

    def __init__(self, item, domain):
        """Get all the data stored for the sensor."""
        self._domain = domain
        self._name = item.get(CONF_NAME)
        self._updateitem = item

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name if self._name is not None else self._item[0]

    @property
    def icon(self):
        """Return the icon for the frontend."""
        return ICON

    @property
    def state(self):
        """Return the sale price of the item."""
        return self._item[1]

    @property
    def entity_picture(self):
        """Return the image."""
        pre_img = self._item[5].split("._",1)[0]+".jpg"
        img = pre_img.split('{\"',1)[1]
        return img

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {'Name': self._item[0],
                 'Category': self._item[2],
                 'Original Price': self._item[3],
                 'Availability': self._item[4],
                 'Item URL': self._item[6]}
        return attrs

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Update all Data every 2h"""
        from lxml import html  
        import requests

        url = "https://www.amazon."+self._updateitem.get(CONF_DOMAIN, self._domain)+"/dp/"+self._updateitem.get(CONF_ASIN)+"/"
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
        page = requests.get(url,headers=headers)
        try:
            #Get all the data from Amazon webpage
            doc = html.fromstring(page.content)
            RAW_NAME = doc.xpath('//h1[@id="title"]//text()')
            RAW_SALE_PRICE = doc.xpath('//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()')
            RAW_CATEGORY = doc.xpath('//a[@class="a-link-normal a-color-tertiary"]//text()')
            RAW_ORIGINAL_PRICE = doc.xpath('//div[@id="price"]/table[@class="a-lineitem"]/tr/td[2]/span[@class="a-text-strike"]/text()')
            RAW_AVAILABILITY = doc.xpath('//div[@id="availability"]//text()')

            #Parse everthing
            NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
            SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
            CATEGORY = ' > '.join([i.strip() for i in RAW_CATEGORY]) if RAW_CATEGORY else None
            ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else None
            AVAILABILITY = ''.join(RAW_AVAILABILITY).strip() if RAW_AVAILABILITY else None

            #Get the Product Image for the Icon
            RAW_IMAGE = doc.xpath('//img[@id="landingImage" and @alt="'+NAME+'"]/@data-a-dynamic-image')
            IMAGE = ' '.join(''.join(RAW_IMAGE).split()) if RAW_IMAGE else None

            if not ORIGINAL_PRICE:
                ORIGINAL_PRICE = SALE_PRICE

            if page.status_code!=200:
                raise ValueError('The requested item page returned: HTTP'+page.status_code+'please check asin and domain ending')

            #Write into variables
            self._item = [NAME, SALE_PRICE, CATEGORY, ORIGINAL_PRICE, AVAILABILITY, IMAGE, url]

            if self._item is None:
                raise ValueError('asin or domain could not be resolved')

        except Exception as e:
            raise ValueError(e)

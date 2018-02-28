#Home-Assistant Config 

This is my implementation of Home-Assistant with a custom amazon_price sensor created by me

To use it simply copy the amazon_price.py from custom_components/sensor/ to your own config dir.

entry in your configuration.yaml

#CONFIGURATION VARIABLES

domain_ending
(string)(Required)The location Part of the amazon url: E.g. com, de, co.uk etc.
    asin: (string)(Required)10 Digit Part of URL mostly after dp surrounded by /
    name: (string)(Optional)The name of the item. If not set, it is parsed from the website.
    domain_ending: (string)(Optional)Overwrite the domain_ending for the current item.

#Example
```yaml
sensor:
  - platform: amazon_price
    domain_ending: 'com'
    items:
      - asin: B077RY9GZD
      - asin: B00ZV9RDKK
        name: "Fire TV Stick"
      - asin: B01CU8JZPU
        name: "Camera"
        domain_ending: 'co.uk'
```


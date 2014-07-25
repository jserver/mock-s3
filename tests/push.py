#!/usr/bin/env python
import boto
from boto.s3.key import Key


OrdinaryCallingFormat = boto.config.get('s3', 'calling_format', 'boto.s3.connection.OrdinaryCallingFormat')

s3 = boto.connect_s3(host='localhost', port=10001, calling_format=OrdinaryCallingFormat, is_secure=False)
b = s3.get_bucket('mocking')

k_cool = Key(b)
k_cool.key = 'cool.html'
k_cool.set_contents_from_string('this is some really cool html')

k_green = Key(b)
k_green.key = 'green.html'
k_green.set_contents_from_string('this is some really good music html')

k_horse = Key(b)
k_horse.key = 'seminoles.html'
k_horse.set_contents_from_string('this is some really seminoles html')

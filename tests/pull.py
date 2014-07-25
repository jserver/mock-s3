#!/usr/bin/env python
import boto
from boto.s3.key import Key


OrdinaryCallingFormat = boto.config.get('s3', 'calling_format', 'boto.s3.connection.OrdinaryCallingFormat')

s3 = boto.connect_s3(host='localhost', port=10001, calling_format=OrdinaryCallingFormat, is_secure=False)
b = s3.get_bucket('mocking')

k_cool = Key(b)
k_cool.key = 'cool.html'
content  = k_cool.get_contents_as_string()
print content

k_green = Key(b)
k_green.key = 'green.html'
content  = k_green.get_contents_as_string()
print content

k_seminoles = Key(b)
k_seminoles.key = 'seminoles.html'
content  = k_seminoles.get_contents_as_string()
print content

k_precise = Key(b)
k_precise.key = 'precise.txt'
content  = k_precise.get_contents_as_string()
print content

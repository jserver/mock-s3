#!/usr/bin/env python
import boto
from boto.s3.key import Key

OrdinaryCallingFormat = boto.config.get('s3', 'calling_format', 'boto.s3.connection.OrdinaryCallingFormat')

s3 = boto.connect_s3(host='localhost', port=10001, calling_format=OrdinaryCallingFormat, is_secure=False)
b = s3.create_bucket('mocking')

kwrite = Key(b)
kwrite.key = 'middle.html'
kwrite.set_contents_from_string('this is some special html')

kread = Key(b)
kread.key = 'middle.html'
content  = kread.get_contents_as_string()
print content

#!/usr/bin/env python
import boto
from boto.s3.key import Key

OrdinaryCallingFormat = boto.config.get('s3', 'calling_format', 'boto.s3.connection.OrdinaryCallingFormat')

s3 = boto.connect_s3(host='localhost', port=10001, calling_format=OrdinaryCallingFormat, is_secure=False)
b = s3.create_bucket('mocking')

keys = b.get_all_keys(prefix='level')
print 'TEST 1'
for key in keys:
    print repr(key)

keys = b.get_all_keys(max_keys=2)
print 'TEST 2'
for key in keys:
    print repr(key)

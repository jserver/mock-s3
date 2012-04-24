#!/usr/bin/env python
import boto
from boto.s3.key import Key


s3 = boto.connect_s3(host='localhost', port=10001, is_secure=False)
b = s3.create_bucket('mocking')

keys = b.get_all_keys()
for key in keys:
    print repr(key)

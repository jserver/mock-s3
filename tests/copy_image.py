#!/usr/bin/env python
import os
import boto
from boto.s3.key import Key


home = os.environ['HOME']

s3 = boto.connect_s3(host='localhost', port=10001, debug=100, is_secure=False)
b = s3.get_bucket('mocking')

dst_bucket = s3.create_bucket('backup')

dst_bucket.copy_key('Pictures/django.jpg', 'mocking', 'Pictures/django.jpg',)

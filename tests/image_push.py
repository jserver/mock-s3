#!/usr/bin/env python
import os
import boto
from boto.s3.key import Key


home = os.environ['HOME']

s3 = boto.connect_s3(host='localhost', port=10001, is_secure=False)
b = s3.get_bucket('mocking')

k_img = Key(b)
k_img.key = 'Pictures/django.jpg'
k_img.set_contents_from_filename('%s/Pictures/django.jpg' % home)

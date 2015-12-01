#!/usr/bin/env python
import os
import boto
from boto.s3.key import Key


home = os.environ['HOME']

OrdinaryCallingFormat = boto.config.get('s3', 'calling_format', 'boto.s3.connection.OrdinaryCallingFormat')

s3 = boto.connect_s3(host='localhost', port=10001, calling_format=OrdinaryCallingFormat, is_secure=False)
b = s3.create_bucket('mockimg')

k_img = Key(b)
k_img.key = 'pics/example.jpg'
k_img.set_contents_from_filename('%s/pics/example.jpg' % home)

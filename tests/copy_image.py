#!/usr/bin/env python
import os
import boto
from boto.s3.key import Key


home = os.environ['HOME']

OrdinaryCallingFormat = boto.config.get('s3', 'calling_format', 'boto.s3.connection.OrdinaryCallingFormat')

s3 = boto.connect_s3(host='localhost', port=10001, calling_format=OrdinaryCallingFormat, is_secure=False)
b = s3.get_bucket('mocking')

dst_bucket = s3.create_bucket('backup')

dst_bucket.copy_key('Pictures/Profile_Crop.jpg', 'mocking', 'Pictures/Profile_Crop.jpg',)

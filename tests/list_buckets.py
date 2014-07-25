#!/usr/bin/env python
import boto


s3 = boto.connect_s3(host='localhost', port=10001, is_secure=False)
for bucket in s3.get_all_buckets():
    print bucket.name, bucket.creation_date

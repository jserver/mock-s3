#!/usr/bin/env python
import boto


s3 = boto.connect_s3(host='localhost', port=10001, is_secure=False)
print s3.get_all_buckets()

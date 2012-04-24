#!/usr/bin/env python
import boto
from boto.s3.key import Key


s3 = boto.connect_s3(host='localhost', port=10001, is_secure=False)
b = s3.create_bucket('mocking')

kwrite = Key(b)
kwrite.key = 'hello.html'
kwrite.set_contents_from_string('this is some really cool html')

kread = Key(b)
kread.key = 'hello.html'
content  = kread.get_contents_as_string()
print content

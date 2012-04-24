class Bucket(object):
    def __init__(self, name, creation_date):
        self.name = name
        self.creation_date = creation_date


class BucketQuery(object):
    def __init__(self, bucket, matches=[], is_truncated=False, **kwargs):
        self.bucket = bucket
        self.matches = matches
        self.is_truncated = is_truncated
        self.marker = kwargs['marker']
        self.prefix = kwargs['prefix']
        self.max_keys = kwargs['max_keys']
        self.delimiter = kwargs['delimiter']


class S3Item(object):
    def __init__(self, key, **kwargs):
        self.key = key
        self.content_type = kwargs['content_type']
        self.md5 = kwargs['md5']
        self.size = kwargs['size']
        if 'creation_date' in kwargs:
            self.creation_date = kwargs['creation_date']
        if 'modified_date' in kwargs:
            self.creation_date = kwargs['modified_date']

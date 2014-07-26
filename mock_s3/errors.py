class NoSuchBucket(Exception):
    def __init__(self):
        self.message = 'The bucket does not exist'
        self.http_status = '404'
    def __str__(self):
        return '%s, %s' % (self.http_status, self.message)


class BucketNotEmpty(Exception):
    def __init__(self):
        self.message = 'The bucket is not empty'
        self.http_status = '409'
    def __str__(self):
        return '%s, %s' % (self.http_status, self.message)

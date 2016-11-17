import ConfigParser
import md5
import os
import shutil
from datetime import datetime

from errors import BucketNotEmpty, NoSuchBucket
from models import Bucket, BucketQuery, S3Item


CONTENT_FILE = '.mocks3_content'
METADATA_FILE = '.mocks3_metadata'


class FileStore(object):
    def __init__(self, root):
        self.root = root
        if not os.path.exists(self.root):
            os.makedirs(self.root)
        self.buckets = self.get_all_buckets()

    def get_bucket_folder(self, bucket_name):
        return os.path.join(self.root, bucket_name)

    def get_all_buckets(self):
        buckets = []
        bucket_list = os.listdir(self.root)
        bucket_list.sort()
        for bucket in bucket_list:
            mtime = os.stat(os.path.join(self.root, bucket)).st_mtime
            create_date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%dT%H:%M:%S.000Z')
            buckets.append(Bucket(bucket, create_date))
        return buckets

    def get_bucket(self, bucket_name):
        for bucket in self.buckets:
            if bucket.name == bucket_name:
                return bucket
        return None

    def create_bucket(self, bucket_name):
        if bucket_name not in [bucket.name for bucket in self.buckets]:
            try:
                os.makedirs(os.path.join(self.root, bucket_name))
            except:
                # mismatch
                pass
            self.buckets = self.get_all_buckets()
        return self.get_bucket(bucket_name)

    def delete_bucket(self, bucket_name):
        bucket = self.get_bucket(bucket_name)
        if not bucket:
            raise NoSuchBucket
        try:
            os.rmdir(os.path.join(self.root, bucket_name))
            self.buckets = self.get_all_buckets()
        except:
            # TODO: for now assume exception is directory is not empty
            raise BucketNotEmpty

    def get_all_keys(self, bucket, **kwargs):
        max_keys = int(kwargs['max_keys'])
        is_truncated = False
        matches = []
        for root, dirs, files in os.walk(os.path.join(self.root, bucket.name)):
            pattern = os.path.join(self.root, bucket.name, kwargs['prefix'])
            if root.startswith(pattern) and METADATA_FILE in files:
                config = ConfigParser.RawConfigParser()
                files_parsed = config.read(os.path.join(root, METADATA_FILE))
                metadata = {}
                if files_parsed:
                    metadata['size'] = config.getint('metadata', 'size')
                    metadata['md5'] = config.get('metadata', 'md5')
                    metadata['content_type'] = config.get('metadata', 'content_type')
                    metadata['creation_date'] = config.get('metadata', 'creation_date')
                    if config.has_option('metadata', 'modified_date'):
                        metadata['modified_date'] = config.get('metadata', 'modified_date')

                actual_key = root.replace(self.root, '', 1)
                actual_key = actual_key.replace('/' + bucket.name + '/', '')
                matches.append(S3Item(actual_key, **metadata))
                if len(matches) >= max_keys:
                    is_truncated = True
                    break
        return BucketQuery(bucket, matches, is_truncated, **kwargs)

    def get_item(self, bucket_name, item_name):
        key_name = os.path.join(bucket_name, item_name)
        dirname = os.path.join(self.root, key_name)
        filename = os.path.join(dirname, CONTENT_FILE)
        metafile = os.path.join(dirname, METADATA_FILE)

        metadata = {}
        config = ConfigParser.RawConfigParser()
        files_parsed = config.read(metafile)
        if files_parsed:
            metadata['size'] = config.getint('metadata', 'size')
            metadata['md5'] = config.get('metadata', 'md5')
            metadata['filename'] = config.get('metadata', 'filename')
            metadata['content_type'] = config.get('metadata', 'content_type')
            metadata['creation_date'] = config.get('metadata', 'creation_date')
            if config.has_option('metadata', 'modified_date'):
                metadata['modified_date'] = config.get('metadata', 'modified_date')

        if not metadata:
            return None

        item = S3Item(key_name, **metadata)
        item.io = open(filename, 'rb')

        return item

    def copy_item(self, src_bucket_name, src_name, bucket_name, name, handler):
        src_key_name = os.path.join(src_bucket_name, src_name)
        src_dirname = os.path.join(self.root, src_key_name)
        src_filename = os.path.join(src_dirname, CONTENT_FILE)
        src_metafile = os.path.join(src_dirname, METADATA_FILE)

        bucket = self.get_bucket(bucket_name)
        key_name = os.path.join(bucket.name, name)
        dirname = os.path.join(self.root, key_name)
        filename = os.path.join(dirname, CONTENT_FILE)
        metafile = os.path.join(dirname, METADATA_FILE)

        if not os.path.exists(dirname):
            os.makedirs(dirname)
        shutil.copy(src_filename, filename)
        shutil.copy(src_metafile, metafile)

        config = ConfigParser.RawConfigParser()
        files_parsed = config.read(metafile)
        metadata = {}
        if files_parsed:
            metadata['size'] = config.getint('metadata', 'size')
            metadata['md5'] = config.get('metadata', 'md5')
            metadata['content_type'] = config.get('metadata', 'content_type')
            metadata['creation_date'] = config.get('metadata', 'creation_date')
            if config.has_option('metadata', 'modified_date'):
                metadata['modified_date'] = config.get('metadata', 'modified_date')

        return S3Item(key_name, **metadata)

    def store_data(self, bucket, item_name, headers, data):
        key_name = os.path.join(bucket.name, item_name)
        dirname = os.path.join(self.root, key_name)
        filename = os.path.join(dirname, CONTENT_FILE)
        metafile = os.path.join(dirname, METADATA_FILE)

        metadata = {}
        config = ConfigParser.RawConfigParser()
        files_parsed = config.read(metafile)
        if files_parsed:
            metadata['size'] = config.getint('metadata', 'size')
            metadata['md5'] = config.get('metadata', 'md5')
            metadata['filename'] = config.get('metadata', 'filename')
            metadata['content_type'] = config.get('metadata', 'content_type')
            metadata['creation_date'] = config.get('metadata', 'creation_date')

        m = md5.new()

        lower_headers = {}
        for key in headers:
            lower_headers[key.lower()] = headers[key]
        headers = lower_headers
        if 'content-type' not in headers:
            headers['content-type'] = 'application/octet-stream'

        size = int(headers['content-length'])
        m.update(data)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(filename, 'wb') as f:
            f.write(data)

        if metadata:
            metadata['md5'] = m.hexdigest()
            metadata['modified_date'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
            metadata['content_type'] = headers['content-type']
            metadata['size'] = size
        else:
            metadata = {
                'content_type': headers['content-type'],
                'creation_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                'md5': m.hexdigest(),
                'filename': filename,
                'size': size,
            }
        config.add_section('metadata')
        config.set('metadata', 'size', metadata['size'])
        config.set('metadata', 'md5', metadata['md5'])
        config.set('metadata', 'filename', metadata['filename'])
        config.set('metadata', 'content_type', metadata['content_type'])
        config.set('metadata', 'creation_date', metadata['creation_date'])
        if 'modified_date' in metadata:
            config.set('metadata', 'modified_date', metadata['modified_date'])
        with open(metafile, 'wb') as configfile:
            config.write(configfile)

        s3_item = S3Item(key, **metadata)
        s3_item.io = open(filename, 'rb')
        return s3_item

    def store_item(self, bucket, item_name, handler):
        key_name = os.path.join(bucket.name, item_name)
        dirname = os.path.join(self.root, key_name)
        filename = os.path.join(dirname, CONTENT_FILE)
        metafile = os.path.join(dirname, METADATA_FILE)

        metadata = {}
        config = ConfigParser.RawConfigParser()
        files_parsed = config.read(metafile)
        if files_parsed:
            metadata['size'] = config.getint('metadata', 'size')
            metadata['md5'] = config.get('metadata', 'md5')
            metadata['filename'] = config.get('metadata', 'filename')
            metadata['content_type'] = config.get('metadata', 'content_type')
            metadata['creation_date'] = config.get('metadata', 'creation_date')

        m = md5.new()

        headers = {}
        for key in handler.headers:
            headers[key.lower()] = handler.headers[key]
        if 'content-type' not in headers:
            headers['content-type'] = 'application/octet-stream'

        size = int(headers['content-length'])
        data = handler.rfile.read(size)
        m.update(data)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(filename, 'wb') as f:
            f.write(data)

        if metadata:
            metadata['md5'] = m.hexdigest()
            metadata['modified_date'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
            metadata['content_type'] = headers['content-type']
            metadata['size'] = size
        else:
            metadata = {
                'content_type': headers['content-type'],
                'creation_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                'md5': m.hexdigest(),
                'filename': filename,
                'size': size,
            }
        if not config.has_section('metadata'):
            config.add_section('metadata')
        config.set('metadata', 'size', metadata['size'])
        config.set('metadata', 'md5', metadata['md5'])
        config.set('metadata', 'filename', metadata['filename'])
        config.set('metadata', 'content_type', metadata['content_type'])
        config.set('metadata', 'creation_date', metadata['creation_date'])
        if 'modified_date' in metadata:
            config.set('metadata', 'modified_date', metadata['modified_date'])
        with open(metafile, 'wb') as configfile:
            config.write(configfile)
        return S3Item(key, **metadata)

    def delete_item(self, bucket_name, item_name):
        dirname = os.path.join(self.root, bucket_name, item_name)
        shutil.rmtree(dirname, ignore_errors=True)

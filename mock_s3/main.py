import argparse
import logging
import os
import sys
import urlparse
import xml.etree.ElementTree as ET
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

from actions import delete_item, delete_items, get_acl, get_item, list_buckets, ls_bucket
from file_store import FileStore


logging.basicConfig(level=logging.INFO)


class S3Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        qs = urlparse.parse_qs(parsed_path.query, True)
        host = self.headers['host'].split(':')[0]
        path = parsed_path.path
        bucket_name = None
        item_name = None
        req_type = None

        mock_hostname = self.server.mock_hostname
        if host != mock_hostname and mock_hostname in host:
            idx = host.index(mock_hostname)
            bucket_name = host[:idx-1]

        if path == '/' and not bucket_name:
            req_type = 'list_buckets'

        else:
            if not bucket_name:
                bucket_name, sep, item_name = path.strip('/').partition('/')
            else:
                item_name = path.strip('/')

            if not bucket_name:
                req_type = 'list_buckets'
            elif not item_name:
                req_type = 'ls_bucket'
            else:
                if 'acl' in qs and qs['acl'] == '':
                    req_type = 'get_acl'
                else:
                    req_type = 'get'

        if req_type == 'list_buckets':
            list_buckets(self)

        elif req_type == 'ls_bucket':
            ls_bucket(self, bucket_name, qs)

        elif req_type == 'get_acl':
            get_acl(self)

        elif req_type == 'get':
            get_item(self, bucket_name, item_name)

        else:
            self.wfile.write('%s: [%s] %s' % (req_type, bucket_name, item_name))

    def do_DELETE(self):
        parsed_path = urlparse.urlparse(self.path)
        qs = urlparse.parse_qs(parsed_path.query, True)
        host = self.headers['host'].split(':')[0]
        path = parsed_path.path
        bucket_name = None
        item_name = None

        mock_hostname = self.server.mock_hostname
        if host != mock_hostname and mock_hostname in host:
            idx = host.index(mock_hostname)
            bucket_name = host[:idx-1]

        if not bucket_name:
            bucket_name, sep, item_name = path.strip('/').partition('/')
        else:
            item_name = path.strip('/')

        if bucket_name and item_name:
            delete_item(self, bucket_name, item_name)
        else:
            self.wfile.write('%s: [%s] %s' % ('DELETE', bucket_name, item_name))

        self.send_response(204)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def do_HEAD(self):
        return self.do_GET()

    def do_POST(self):
        parsed_path = urlparse.urlparse(self.path)
        qs = urlparse.parse_qs(parsed_path.query, True)
        host = self.headers['host'].split(':')[0]
        path = parsed_path.path
        bucket_name = None
        item_name = None
        req_type = None

        mock_hostname = self.server.mock_hostname
        if host != mock_hostname and mock_hostname in host:
            idx = host.index(mock_hostname)
            bucket_name = host[:idx-1]

        if path == '/' and bucket_name and 'delete' in qs:
            req_type = 'delete_keys'

        else:
            if not bucket_name:
                bucket_name, sep, item_name = path.strip('/').partition('/')
            else:
                item_name = path.strip('/')

            if not item_name and 'delete' in qs:
                req_type = 'delete_keys'

        if req_type == 'delete_keys':
            size = int(self.headers['content-length'])
            data = self.rfile.read(size)
            root = ET.fromstring(data)
            keys = []
            for obj in root.findall('Object'):
                keys.append(obj.find('Key').text)
            delete_items(self, bucket_name, keys)
        else:
            self.wfile.write('%s: [%s] %s' % (req_type, bucket_name, item_name))

    def do_PUT(self):
        parsed_path = urlparse.urlparse(self.path)
        qs = urlparse.parse_qs(parsed_path.query, True)
        host = self.headers['host'].split(':')[0]
        path = parsed_path.path
        bucket_name = None
        item_name = None
        req_type = None

        mock_hostname = self.server.mock_hostname
        if host != mock_hostname and mock_hostname in host:
            idx = host.index(mock_hostname)
            bucket_name = host[:idx-1]

        if path == '/' and bucket_name:
            req_type = 'create_bucket'

        else:
            if not bucket_name:
                bucket_name, sep, item_name = path.strip('/').partition('/')
            else:
                item_name = path.strip('/')

            if not item_name:
                req_type = 'create_bucket'
            else:
                if 'acl' in qs and qs['acl'] == '':
                    req_type = 'set_acl'
                else:
                    req_type = 'store'

        if 'x-amz-copy-source' in self.headers:
            copy_source = self.headers['x-amz-copy-source']
            src_bucket, sep, src_key = copy_source.partition('/')
            req_type = 'copy'

        if req_type == 'create_bucket':
            self.server.file_store.create_bucket(bucket_name)
            self.send_response(200)

        elif req_type == 'store':
            bucket = self.server.file_store.get_bucket(bucket_name)
            if not bucket:
                # TODO: creating bucket for now, probably should return error
                bucket = self.server.file_store.create_bucket(bucket_name)
            item = self.server.file_store.store_item(bucket, item_name, self)
            self.send_response(200)
            self.send_header('Etag', '"%s"' % item.md5)

        elif req_type == 'copy':
            self.server.file_store.copy_item(src_bucket, src_key, bucket_name, item_name, self)
            # TODO: should be some xml here
            self.send_response(200)

        self.send_header('Content-Type', 'text/xml')
        self.end_headers()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    def set_file_store(self, file_store):
        self.file_store = file_store

    def set_mock_hostname(self, mock_hostname):
        self.mock_hostname = mock_hostname

    def set_pull_from_aws(self, pull_from_aws):
        self.pull_from_aws = pull_from_aws


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='A Mock-S3 server.')
    parser.add_argument('--hostname', dest='hostname', action='store',
                        default='localhost',
                        help='Hostname to listen on.')
    parser.add_argument('--port', dest='port', action='store',
                        default=10001, type=int,
                        help='Port to run server on.')
    parser.add_argument('--root', dest='root', action='store',
                        default='%s/s3store' % os.environ['HOME'],
                        help='Defaults to $HOME/s3store.')
    parser.add_argument('--pull-from-aws', dest='pull_from_aws', action='store_true',
                        default=False,
                        help='Pull non-existent keys from aws.')
    args = parser.parse_args()

    server = ThreadedHTTPServer((args.hostname, args.port), S3Handler)
    server.set_file_store(FileStore(args.root))
    server.set_mock_hostname(args.hostname)
    server.set_pull_from_aws(args.pull_from_aws)

    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

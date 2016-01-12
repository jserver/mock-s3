import urllib2
import datetime

import xml_templates


def list_buckets(handler):
    handler.send_response(200)
    handler.send_header('Content-Type', 'application/xml')
    handler.end_headers()
    buckets = handler.server.file_store.buckets
    xml = ''
    for bucket in buckets:
        xml += xml_templates.buckets_bucket_xml.format(bucket=bucket)
    xml = xml_templates.buckets_xml.format(xml)
    handler.wfile.write(xml)


def ls_bucket(handler, bucket_name, qs):
    bucket = handler.server.file_store.get_bucket(bucket_name)
    if bucket:
        kwargs = {
            'marker': qs.get('marker', [''])[0],
            'prefix': qs.get('prefix', [''])[0],
            'max_keys': qs.get('max-keys', [1000])[0],
            'delimiter': qs.get('delimiter', [''])[0],
        }
        bucket_query = handler.server.file_store.get_all_keys(bucket, **kwargs)
        handler.send_response(200)
        handler.send_header('Content-Type', 'application/xml')
        handler.end_headers()
        contents = ''
        for s3_item in bucket_query.matches:
            contents += xml_templates.bucket_query_content_xml.format(s3_item=s3_item)
        xml = xml_templates.bucket_query_xml.format(bucket_query=bucket_query, contents=contents)
        handler.wfile.write(xml)
    else:
        handler.send_response(404)
        handler.send_header('Content-Type', 'application/xml')
        handler.end_headers()
        xml = xml_templates.error_no_such_bucket_xml.format(name=bucket_name)
        handler.wfile.write(xml)


def get_acl(handler):
    handler.send_response(200)
    handler.send_header('Content-Type', 'application/xml')
    handler.end_headers()
    handler.wfile.write(xml_templates.acl_xml)


def load_from_aws(handler, bucket_name, item_name):
    bucket = handler.server.file_store.get_bucket(bucket_name)
    aws_url = "http://s3.amazonaws.com/%s/%s" % (bucket_name, item_name)
    response = urllib2.urlopen(aws_url)
    data = response.read()
    response_headers = response.info()
    return handler.server.file_store.store_data(bucket, item_name, response_headers, data)


def get_item(handler, bucket_name, item_name):
    item = handler.server.file_store.get_item(bucket_name, item_name)
    if not item and handler.server.pull_from_aws:
            item = load_from_aws(handler, bucket_name, item_name)
    if not item:
        handler.send_response(404, '')
        return

    content_length = item.size

    headers = {}
    for key in handler.headers:
        headers[key.lower()] = handler.headers[key]

    if hasattr(item, 'creation_date'):
        last_modified = item.creation_date
    else:
        last_modified = item.modified_date
    last_modified = datetime.datetime.strptime(last_modified, '%Y-%m-%dT%H:%M:%S.000Z')
    last_modified = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')

    if 'range' in headers:
        handler.send_response(206)
        handler.send_header('Content-Type', item.content_type)
        handler.send_header('Last-Modified', last_modified)
        handler.send_header('Etag', item.md5)
        handler.send_header('Accept-Ranges', 'bytes')
        range_ = handler.headers['bytes'].split('=')[1]
        start = int(range_.split('-')[0])
        finish = int(range_.split('-')[1])
        if finish == 0:
            finish = content_length - 1
        bytes_to_read = finish - start + 1
        handler.send_header('Content-Range', 'bytes %s-%s/%s' % (start, finish, content_length))
        handler.end_headers()
        item.io.seek(start)
        handler.wfile.write(item.io.read(bytes_to_read))
        return

    handler.send_response(200)
    handler.send_header('Last-Modified', last_modified)
    handler.send_header('Etag', item.md5)
    handler.send_header('Accept-Ranges', 'bytes')
    handler.send_header('Content-Type', item.content_type)
    handler.send_header('Content-Length', content_length)
    handler.end_headers()
    if handler.command == 'GET':
        handler.wfile.write(item.io.read())


def delete_item(handler, bucket_name, item_name):
    handler.server.file_store.delete_item(bucket_name, item_name)


def delete_items(handler, bucket_name, keys):
    handler.send_response(200)
    handler.send_header('Content-Type', 'application/xml')
    handler.end_headers()
    xml = ''
    for key in keys:
        delete_item(handler, bucket_name, key)
        xml += xml_templates.deleted_deleted_xml.format(key=key)
    xml = xml_templates.deleted_xml.format(contents=xml)
    handler.wfile.write(xml)

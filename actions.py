import urllib2


def list_buckets(handler):
    handler.send_response(200)
    handler.send_header('Content-Type', 'application/xml')
    handler.end_headers()
    buckets = handler.server.file_store.buckets
    template = handler.server.env.get_template('buckets.xml')
    handler.wfile.write(template.render(buckets=buckets))


def ls_bucket(handler, bucket_name, qs):
    bucket = handler.server.file_store.get_bucket(bucket_name)
    if bucket:
        kwargs = {
            'marker': getattr(qs, 'marker', [''])[0],
            'prefix': getattr(qs, 'prefix', [''])[0],
            'max_keys': getattr(qs, 'max-keys', [1000])[0],
            'delimiter': getattr(qs, 'delimiter', [''])[0],
        }
        bucket_query = handler.server.file_store.get_all_keys(bucket, **kwargs)
        handler.send_response(200)
        handler.send_header('Content-Type', 'application/xml')
        handler.end_headers()
        template = handler.server.env.get_template('bucket_query.xml')
        handler.wfile.write(template.render(bucket_query=bucket_query))
    else:
        handler.send_response(404)
        handler.send_header('Content-Type', 'application/xml')
        handler.end_headers()
        template = handler.server.env.get_template('error_no_such_bucket.xml')
        handler.wfile.write(template.render(name=bucket_name))


def get_acl(handler):
    handler.send_response(200)
    handler.send_header('Content-Type', 'application/xml')
    handler.end_headers()
    template = handler.server.env.get_template('acl.xml')
    handler.wfile.write(template.render())


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
    if 'range' in headers:
        handler.send_response(206)
        handler.send_header('Content-Type', item.content_type)
        handler.send_header('Etag', item.md5)
        handler.send_header('Accept-Ranges', 'bytes')
        range = handler.headers['bytes'].split('=')[1]
        start = int(range.split('-')[0])
        finish = int(range.split('-')[1])
        if finish == 0:
            finish =  content_length - 1
        bytes_to_read = finish - start + 1
        handler.send_header('Content-Range', 'bytes %s-%s/%s' % (start, finish, content_length))
        handler.end_headers()
        item.io.seek(start)
        handler.wfile.write(item.io.read(bytes_to_read))
        return

    handler.send_response(200)
    handler.send_header('Content-Type', item.content_type)
    handler.send_header('Etag', item.md5)
    handler.send_header('Accept-Ranges', 'bytes')
    handler.send_header('Content-Length', content_length)
    handler.end_headers()
    if handler.command == 'GET':
        handler.wfile.write(item.io.read())

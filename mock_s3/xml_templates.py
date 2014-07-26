
buckets_xml = '''<?xml version='1.0' encoding='UTF-8'?>
<ListAllMyBucketsResult xmlns="http://doc.s3.amazonaws.com/2006-03-01">
  <Owner>
    <ID>123</ID>
    <DisplayName>MockS3</DisplayName>
  </Owner>
  <Buckets>
    {}
  </Buckets>
</ListAllMyBucketsResult>'''

buckets_bucket_xml = '''    <Bucket>
      <Name>{bucket.name}</Name>
      <CreationDate>{bucket.creation_date}</CreationDate>
    </Bucket>'''

bucket_query_xml = '''<?xml version='1.0' encoding='UTF-8'?>
<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01">
  <Name>{bucket_query.bucket.name}</Name>
  <Prefix>{bucket_query.prefix}</Prefix>
  <Marker>{bucket_query.marker}</Marker>
  <MaxKeys>{bucket_query.max_keys}</MaxKeys>
  <IsTruncated>false</IsTruncated>
  {contents}
</ListBucketResult>'''

bucket_query_content_xml = '''  <Contents>
    <Key>{s3_item.key}</Key>
    <LastModified>{s3_item.creation_date}</LastModified>
    <ETag>&quot;{s3_item.md5}&quot;</ETag>
    <Size>{s3_item.size}</Size>
    <StorageClass>STANDARD</StorageClass>
    <Owner>
      <ID>123</ID>
      <DisplayName>MockS3</DisplayName>
    </Owner>
  </Contents>'''

error_no_such_bucket_xml = '''<?xml version='1.0' encoding='UTF-8'?>
<Error>
  <Code>NoSuchBucket</Code>
  <Message>The resource you requested does not exist</Message>
  <Resource>{name}</Resource>
  <RequestId>1</RequestId>
</Error>'''

acl_xml = '''<?xml version='1.0' encoding='UTF-8'?>
<AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01">
  <Owner>
    <ID>123</ID>
    <DisplayName>MockS3</DisplayName>
  </Owner>
  <AccessControlList>
    <Grant>
      <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">
        <ID>abc</ID>
        <DisplayName>You</DisplayName>
      </Grantee>
      <Permission>FULL_CONTROL</Permission>
    </Grant>
  </AccessControlList>
</AccessControlPolicy>'''

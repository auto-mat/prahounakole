from storages.backends.s3boto3 import S3Boto3Storage


class AwsS3MediaStorage(S3Boto3Storage):
    default_acl = 'public-read'
    file_overwrite = False

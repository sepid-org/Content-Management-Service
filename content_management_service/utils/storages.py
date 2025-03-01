from storages.backends.s3boto3 import S3Boto3Storage


class PublicS3Storage(S3Boto3Storage):
    location = 'cms'
    default_acl = 'public-read'  # Set ACL to public-read
    file_overwrite = False  # Prevent overwriting files with the same name


class StaticS3Storage(S3Boto3Storage):
    default_acl = 'public-read'
    file_overwrite = False
    location = 'static'

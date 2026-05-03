import oss2
from django.conf import settings


def get_oss_bucket():
    auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)
    return oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)


def generate_presigned_url(oss_key, expires=60, process=None):
    bucket = get_oss_bucket()
    params = {}
    if process:
        params['x-oss-process'] = process
    return bucket.sign_url('GET', oss_key, expires, params=params)


def get_thumbnail_url(oss_key, size=400):
    return generate_presigned_url(oss_key, process=f'image/resize,w_{size}')

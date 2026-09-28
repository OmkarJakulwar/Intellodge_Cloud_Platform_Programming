# intelrev/services/s3_setup.py
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import django
from django.conf import settings
from intellodge_core.logger import get_logger
import mimetypes
import os
import io
from PIL import Image

log = get_logger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "intellodge.settings")
django.setup()


def get_s3_client():
    session = boto3.Session(region_name=getattr(settings, "AWS_REGION", "us-east-1"))
    return session.client("s3")


def upload_fileobj(fileobj, key, bucket_name=None):
    # this function will upload the images to s3 bucket
    if bucket_name is None:
        bucket_name = getattr(settings, "AWS_S3_BUCKET", None)
    client = get_s3_client()

    content_type = getattr(fileobj, "content_type", None) or mimetypes.guess_type(key)[0] or "application/octet-stream"
    extra_args = {"ContentType": content_type}

    try:
        client.upload_fileobj(fileobj, bucket_name, key, ExtraArgs=extra_args)
    except ClientError as e:
        log.error("S3 upload error:", e)
        raise

    region = getattr(settings, "AWS_REGION", "us-east-1")
    if region == "us-east-1":
        url = f"https://{bucket_name}.s3.amazonaws.com/{key}"
    else:
        url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{key}"
    return url


def list_s3_images(prefix=None, bucket_name=None):
    # It List all image paths (public URLs) directly from S3.
    if bucket_name is None:
        bucket_name = getattr(settings, "AWS_S3_BUCKET", None)

    client = get_s3_client()
    params = {"Bucket": bucket_name}
    if prefix:
        params["Prefix"] = prefix

    try:
        response = client.list_objects_v2(**params)
        contents = response.get("Contents", [])
        region = getattr(settings, "AWS_REGION", "us-east-1")

        base_url = (
            f"https://{bucket_name}.s3.amazonaws.com"
            if region == "us-east-1"
            else f"https://{bucket_name}.s3.{region}.amazonaws.com"
        )

        # Return URLs for all image files
        return [
            f"{base_url}/{item['Key']}"
            for item in contents
            if item["Key"].lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
        ]
    except ClientError as e:
        log.error("S3 list error:", e)
        return []
        
def delete_s3_image(key, bucket_name=None):
    # Delete a single image from S3 using the key.
    if bucket_name is None:
        bucket_name = getattr(settings, "AWS_S3_BUCKET", None)

    client = get_s3_client()

    try:
        client.delete_object(Bucket=bucket_name, Key=key)
        log.info(f"Deleted S3 image: s3://{bucket_name}/{key}")
        return True

    except ClientError as e:
        log.error(f"Failed to delete S3 image {key}: {e}")
        return False
        
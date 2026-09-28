# s3_create_bucket.py
import os
import sys
import django
from django.conf import settings
import boto3
from botocore.exceptions import ClientError

# Setup Django settings
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "intellodge.settings")  
django.setup()

# Create bucket function
def create_bucket():
    bucket_name = getattr(settings, "AWS_S3_BUCKET", "intellodge-room-images-demo-intelroom")
    if not bucket_name:
        raise ValueError("AWS_S3_BUCKET is not defined in settings.py")

    region = getattr(settings, "AWS_REGION", "us-east-1")
    s3 = boto3.client("s3", region_name=region)

    try:
        if region == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region}
            )
        print(f"Bucket '{bucket_name}' created successfully in region '{region}'.")
        return True

    except ClientError as e:
        print(f"Error creating bucket '{bucket_name}': {e}")
        return False


# Running script
if __name__ == "__main__":
    result = create_bucket()
    print(result)

import boto3
import subprocess
import zipfile
import os
from pathlib import Path
import shutil
from intellodge_core.logger import get_logger

AWS_REGION = "us-east-1"
EXISTING_LAMBDA_ROLE_ARN = "arn:aws:iam::414333503877:role/LabRole"

lambda_client = boto3.client("lambda", region_name=AWS_REGION)
events_client = boto3.client("events", region_name=AWS_REGION)

LAMBDA_FUNCTION_NAME = "AutoRoomStatusLambda"
RULE_NAME = "DailyRoomStatusUpdateRule"

# Paths
BASE_DIR = Path(__file__).parent
LAMBDA_CODE_DIR = BASE_DIR / "lambda_code"
LAMBDA_FILE = LAMBDA_CODE_DIR / "auto_room_status.py"
REQUIREMENTS_FILE = LAMBDA_CODE_DIR / "requirements_lambda.txt"
BUILD_DIR = BASE_DIR.parent / "lambda_build"
ZIP_PATH = BASE_DIR.parent / "AutoRoomStatusLambda.zip"

log = get_logger(__name__)


def build_lambda_package():
    # Install dependencies and bundle the Lambda function.
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR, exist_ok=True)

    log.info(" Installing dependencies...")
    subprocess.check_call([
        "pip", "install", "-r", str(REQUIREMENTS_FILE),
        "-t", str(BUILD_DIR)
    ])

    shutil.copy(LAMBDA_FILE, BUILD_DIR / "lambda_function.py")

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(BUILD_DIR):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, start=BUILD_DIR)
                zf.write(filepath, arcname)

    log.info(f" Lambda package created at: {ZIP_PATH}")


def create_or_update_lambda(zip_path: Path):
    # Create or update the Lambda function.
    with open(zip_path, "rb") as f:
        zip_bytes = f.read()

    try:
        response = lambda_client.create_function(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Runtime="python3.9",
            Role=EXISTING_LAMBDA_ROLE_ARN,
            Handler="lambda_function.lambda_handler",
            Code={"ZipFile": zip_bytes},
            Description="Automatically updates room status daily",
            Timeout=15,
            MemorySize=128,
            Publish=True,
        )
        log.info(f" Created new Lambda: {response['FunctionArn']}")
        return response["FunctionArn"]
    except lambda_client.exceptions.ResourceConflictException:
        response = lambda_client.update_function_code(
            FunctionName=LAMBDA_FUNCTION_NAME,
            ZipFile=zip_bytes,
            Publish=True,
        )
        log.info(f" Updated existing Lambda: {response['FunctionArn']}")
        return response["FunctionArn"]


if __name__ == "__main__":
    log.info("=== Building and Deploying AutoRoomStatusLambda ===")
    build_lambda_package()
    function_arn = create_or_update_lambda(ZIP_PATH)
    log.info("Deployment complete!")

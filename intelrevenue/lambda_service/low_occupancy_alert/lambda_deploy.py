import boto3

lambda_client = boto3.client("lambda", region_name="us-east-1")
with open("low_occupancy_direct.zip", "rb") as f:
    zipped_code = f.read()

function_name = "LowOccupancyAlert"
role_arn = "arn:aws:iam::414333503877:role/LabRole"

# Check if function exists or not
try:
    lambda_client.get_function(FunctionName=function_name)
    exists = True
except lambda_client.exceptions.ResourceNotFoundException:
    exists = False

if exists:
    response = lambda_client.update_function_code(
        FunctionName=function_name,
        ZipFile=zipped_code,
        Publish=True
    )
    print("Lambda updated:", response)
else:
    response = lambda_client.create_function(
        FunctionName=function_name,
        Runtime="python3.11",
        Role=role_arn,
        Handler="lambda_function.lambda_handler",
        Code={"ZipFile": zipped_code},
        Timeout=30,
        MemorySize=128,
        Description="Directly publishes to SNS from Lambda"
    )
    print("Lambda created:", response)

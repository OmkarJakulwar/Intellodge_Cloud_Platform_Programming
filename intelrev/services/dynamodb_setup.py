import boto3
from botocore.exceptions import ClientError
from django.conf import settings

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def get_dynamodb_resource():
    # getting connected to the dynamodb session using the lab role
    
    session = boto3.Session(region_name='us-east-1')
    return session.resource("dynamodb")

def create_table(table_name, key_schema, attribute_definitions):
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            BillingMode='PAY_PER_REQUEST'
        )
        
        print(f"Creating table '{table_name}'...")
        table.wait_until_exists()
        print(f"Table '{table_name}' is ready!")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table '{table_name}' already exists.")
        else:
            print(f"Error creating table: {e.response['Error']['Message']}")

if __name__ == "__main__":
    # Create Users 
    create_table(
        'Users',
        key_schema=[{'AttributeName': 'cognito_sub', 'KeyType': 'HASH'}],
        attribute_definitions=[{'AttributeName': 'cognito_sub', 'AttributeType': 'S'}]
    )
    
    # Create Rooms table
    create_table(
        'Rooms',
        key_schema=[{'AttributeName': 'room_number', 'KeyType': 'HASH'}],  # partition key
        attribute_definitions=[{'AttributeName': 'room_number', 'AttributeType': 'S'}]
    )
    
    # Create Bookings table
    create_table(
        'Bookings',
        key_schema=[{'AttributeName': 'booking_id', 'KeyType': 'HASH'}],  # partition key
        attribute_definitions=[{'AttributeName': 'booking_id', 'AttributeType': 'S'}]
    )

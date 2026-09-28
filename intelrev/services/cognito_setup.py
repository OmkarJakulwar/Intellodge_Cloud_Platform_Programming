import boto3

client = boto3.client('cognito-idp', region_name='us-east-1')

# To create a user pool
response = client.create_user_pool(
    PoolName='IntellodgeUserPool',
    Policies={
        'PasswordPolicy': {
            'MinimumLength': 8,
            'RequireUppercase': True,
            'RequireLowercase': True,
            'RequireNumbers': True,
            'RequireSymbols': True
        }
    }
)
user_pool_id = response['UserPool']['Id']
print("User pool created:", user_pool_id)

# To create app client for the pool
client_response = client.create_user_pool_client(
    UserPoolId=user_pool_id,
    ClientName='IntellodgeAppClient',
    GenerateSecret=False,
    ExplicitAuthFlows=['ALLOW_USER_PASSWORD_AUTH', 'ALLOW_REFRESH_TOKEN_AUTH']
)
client_id = client_response['UserPoolClient']['ClientId']
print("App client created:", client_id)

import boto3
from botocore.exceptions import ClientError
from django.conf import settings

class CognitoService:
    def __init__(self):
        self.client = boto3.client('cognito-idp', region_name='us-east-1')
        self.user_pool_id = getattr(settings, "COGNITO_USER_POOL_ID")
        self.client_id = getattr(settings, "COGNITO_CLIENT_ID")

    # User Signup via Cognito authentication
    def sign_up(self, username, password, email):
        try:
            resp = self.client.sign_up(
                ClientId=self.client_id,
                Username=username,
                Password=password,
                UserAttributes=[{'Name': 'email', 'Value': email}]
            )
            return {'success': True, 'user_sub': resp['UserSub']}
        except ClientError as e:
            return {'success': False, 'error': str(e)}
    
    # To Confirm the above user to signup this method confirms the user without sending email to the user.
    def admin_confirm_sign_up(self, username):
        """Force-confirm a user (bypass email/SMS verification)"""
        try:
            self.client.admin_confirm_sign_up(
                UserPoolId=self.user_pool_id,
                Username=username
            )
            return {"success": True, "message": f"User {username} confirmed successfully."}
        except ClientError as e:
            return {"success": False, "error": e.response["Error"]["Message"]}
    
    # User Signin via Cognito authentication
    def sign_in(self, username, password):
        try:
            resp = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={'USERNAME': username, 'PASSWORD': password}
            )
            return {
                'success': True,
                'id_token': resp['AuthenticationResult']['IdToken']
            }
        except ClientError as e:
            return {'success': False, 'error': str(e)}


from intelrev.services.dynamodb_setup import get_dynamodb_resource
from botocore.exceptions import ClientError
from intellodge_core.base_service import BaseDynamoDBService
from intellodge_core.logger import get_logger
from intellodge_core.datetime_utils import now_utc
from intellodge_core.exceptions import NotFoundError, ValidationError

log = get_logger(__name__)

class DynamoUserProfile(BaseDynamoDBService):
    """DynamoDB user profile linked to Cognito sub"""
    
    # Using BaseDynamoDBService to connect to the Users table
    def __init__(self):
        super().__init__("Users") 
    
    
    def create(self, cognito_sub, username, firstname, lastname, gender, email, role="user"):
        """Create user profile record in DynamoDB"""
        item = {
            'cognito_sub': cognito_sub,
            'username': username,
            'firstname': firstname,
            'lastname': lastname,
            'gender': gender,
            'email': email,
            'role': role,
            "created_at": now_utc()
        }
        
        result = super().create(item)
        created_item = result.get("item")
        if not created_item:
            raise ValueError("Failed to create user in DynamoDB.")

        log.info(f"User created: {username} ({cognito_sub})")
        return created_item

    def get_by_cognito_sub(self, cognito_sub):
        """Fetch user profile by Cognito sub"""
        try:
            response = self.read({'cognito_sub': cognito_sub})
            if not response.get("success") or not response.get("item"):
                raise NotFoundError(f"User with cognito_sub {cognito_sub} not found")
            return response["item"]
        except ClientError as e:
            print("Error fetching user:", e)
            return None

def update(self, key_dict: dict, update_fields: dict):
        #  Update fields for a user in DynamoDB.
        
        try:
            # DynamoDB UpdateExpression
            update_expr = "SET " + ", ".join(f"{k}=:{k}" for k in update_fields.keys())
            expr_attr_vals = {f":{k}": v for k, v in update_fields.items()}

            resp = self.table.update_item(
                Key=key_dict,
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_attr_vals,
                ReturnValues="ALL_NEW"
            )
            return {"success": True, "item": resp.get("Attributes")}
        except ClientError as e:
            log.error(f"Failed to update user {key_dict}: {e}")
            return {"success": False, "error": str(e)}
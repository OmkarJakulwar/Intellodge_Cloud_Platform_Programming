from botocore.exceptions import ClientError
import boto3
from .logger import get_logger

logger = get_logger(__name__)

class BaseDynamoDBService:
    def __init__(self, table_name, region_name="us-east-1"):
        self.dynamodb = boto3.resource("dynamodb", region_name=region_name)
        self.table = self.dynamodb.Table(table_name)
        self.logger = get_logger(f"intellodge.{table_name}")

    def create(self, item):
        try:
            self.table.put_item(Item=item)
            self.logger.info(f"Created item: {item}")
            return {"success": True, "message": "Item created successfully", "item": item}
        except ClientError as e:
            self.logger.error(f"Create failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def read(self, key):
        try:
            response = self.table.get_item(Key=key)
            item = response.get("Item")
            if not item:
                return {"success": False, "error": "Item not found"}
            self.logger.info(f"📄 Read item: {item}")
            return {"success": True, "item": item}
        except ClientError as e:
            self.logger.error(f"❌ Read failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def update(self, key, updates):
        # Handle reserved keywords safely
        expression_attribute_names = {}
        update_parts = []
        expression_attribute_values = {}

        for attr, value in updates.items():
            placeholder_name = f"#{attr}"
            placeholder_value = f":{attr}"

            expression_attribute_names[placeholder_name] = attr
            expression_attribute_values[placeholder_value] = value

            update_parts.append(f"{placeholder_name} = {placeholder_value}")

        update_expression = "SET " + ", ".join(update_parts)

        try:
            self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
            )
            self.logger.info(f"Updated key: {key} with updates {updates}")
            return {"success": True, "message": "Item updated successfully", "updated_fields": updates}
        except Exception as e:
            self.logger.error(f"Update failed: {key}: {str(e)}")
            return {"success": False, "error": str(e)}


    def delete(self, key):
        try:
            self.table.delete_item(Key=key)
            self.logger.info(f"Deleted item with key {key}")
            return {"success": True, "message": "Item deleted successfully"}
        except ClientError as e:
            self.logger.error(f"Delete failed: {str(e)}")
            return {"success": False, "error": str(e)}
        
    def find_all(self):
        """Return all items from the table."""
        try:
            response = self.table.scan()
            items = response.get("Items", [])
            self.logger.info(f"📦 Retrieved {len(items)} items")
            return {"success": True, "items": items}
        except ClientError as e:
            self.logger.error(f"❌ Scan failed: {str(e)}")
            return {"success": False, "error": str(e)}
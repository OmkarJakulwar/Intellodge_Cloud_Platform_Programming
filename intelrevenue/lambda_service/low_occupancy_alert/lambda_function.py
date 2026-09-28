import boto3
import os
import logging
from datetime import datetime

# DynamoDB table containing rooms
ROOMS_TABLE = os.environ.get("ROOMS_TABLE", "Rooms")
SNS_TOPIC_ARN = os.environ.get(
    "SNS_TOPIC_ARN",
    "arn:aws:sns:us-east-1:414333503877:low-occupancy-alert"
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
sns_client = boto3.client("sns", region_name="us-east-1")
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
rooms_table = dynamodb.Table(ROOMS_TABLE)

def lambda_handler(event, context):
    """
    Automatic low occupancy alert:
    - Reads rooms from DynamoDB
    - Calculates occupancy
    - Publishes to SNS if occupancy < threshold
    """
    threshold = 30

    try:
        resp = rooms_table.scan()
        rooms = resp.get("Items", [])
        total_rooms = len(rooms)
        occupied_rooms = len([r for r in rooms if r.get("status") == "Occupied"])
        occupancy = round((occupied_rooms / total_rooms) * 100, 2) if total_rooms else 0

        logger.info(f"Current occupancy: {occupancy}%")

        if occupancy < threshold:
            subject = "Intellodge Alert: Low Occupancy Warning"
            message = (
                f"LOW OCCUPANCY ALERT\n\n"
                f"Current Occupancy: {occupancy}%\n"
                f"Threshold: {threshold}%\n\n"
                f"Please take immediate actions to improve occupancy.\n"
                f"Generated at {datetime.utcnow().isoformat()} UTC"
            )
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=subject,
                Message=message
            )
            logger.info("SNS alert published successfully!")
            return {"success": True, "occupancy": occupancy}

        return {"success": False, "occupancy": occupancy}

    except Exception as e:
        logger.error(f"Error in low occupancy alert Lambda: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
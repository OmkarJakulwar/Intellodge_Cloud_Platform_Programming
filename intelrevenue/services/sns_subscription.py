import boto3
from botocore.exceptions import ClientError
from intellodge_core.logger import get_logger
from intelrev.models.dynamo_user_profile import DynamoUserProfile

logger = get_logger(__name__)
sns = boto3.client("sns", region_name="us-east-1")

# Instantiate user service
user_service = DynamoUserProfile()

LOW_OCC_TOPIC_ARN = "arn:aws:sns:us-east-1:414333503877:low-occupancy-alert"


def subscribe_admin_to_alerts(profile):
    # Automatically subscribe admin to alert topics only once.
    
    email = profile["email"]
    cognito_sub = profile["cognito_sub"]

    # Check if already subscribed
    if profile.get("sns_subscribed", False):
        logger.info(f"[SNS] Admin already subscribed → {email}")
        return {"success": True, "message": "Already subscribed"}

    # Subscribe email to SNS
    try:
        sns.subscribe(
            TopicArn=LOW_OCC_TOPIC_ARN,
            Protocol="email",
            Endpoint=email,
            ReturnSubscriptionArn=False
        )
        logger.info(f"[SNS] Subscription request sent → {email}")

        # Update DynamoDB flag to prevent future subscriptions
        user_service.update({"cognito_sub": cognito_sub}, {"sns_subscribed": True})
        logger.info(f"[SNS] Subscription confirmed in DB → {email}")

        return {"success": True, "message": "Subscription request sent"}

    except Exception as e:
        logger.error(f"[SNS] Subscription failed → {e}")
        return {"success": False, "error": str(e)}

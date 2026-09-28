#Here we are sending the low occupancy & revenue drop alerts email to the admin users.

import boto3
from intellodge_core.logger import get_logger
from revenue_services import RevenueService 

logger = get_logger(__name__)
sns = boto3.client("sns", region_name="us-east-1")

LOW_OCC_TOPIC_ARN = "arn:aws:sns:us-east-1:414333503877:low-occupancy-alert"


# this will publish the email to the subscriber
def publish_email(topic_arn: str, subject: str, message: str):
    try:
        resp = sns.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message
        )
        logger.info(f"SNS Email Published → {topic_arn}")
        return resp
    except Exception as e:
        logger.error(f"Failed to send SNS email: {e}")
        raise

# Below is the alert service class which contains main alert logic
class AlertService:
    def __init__(self, revenue_service):
        self.rev = revenue_service

    # Low Occupancy Alert
    def send_low_occupancy_alert(self, threshold=30):
        occupancy = self.rev.occupancy_rate()

        if occupancy < threshold:
            subject = "Intellodge Alert: Low Occupancy Warning"
            message = (
            f"LOW OCCUPANCY ALERT\n"
            f"\n\n"
            f"Dear Intellodge Administrator,\n\n"
            f"Our monitoring system has detected 'low occupancy levels' "
            f"at our Intellodge Hotel.\n\n"

            f"- Current Status of this month \n"
            f"- Current Occupancy: {occupancy}% \n"
            f"- Alert Threshold: {threshold}% \n\n"
            f" Please take some actions as soon as posible to improve our occupancy rate...!! \n\n"
            "Recommended Actions:\n"
            "- Adjust pricing\n"
            "- Launch promotions\n"
            "- Review booking patterns\n\n"
    
            f"Regards,\n"
            f"Intellodge Automated Alert System"
            )
            
            publish_email(LOW_OCC_TOPIC_ARN, subject, message,)
            return {"success": True, "occupancy": occupancy}
            
        return {"success": False, "occupancy": occupancy}

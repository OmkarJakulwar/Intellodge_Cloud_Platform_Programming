import boto3

LAMBDA_FUNCTION_NAME = "LowOccupancyAlert"   
RULE_NAME = "LowOccupancyDailyTrigger"
SCHEDULE_EXPRESSION = "cron(0 8 * * ? *)"  # 8 AM UTC

events = boto3.client("events", region_name="us-east-1")
lambda_client = boto3.client("lambda", region_name="us-east-1")

def create_eventbridge_rule():
    print("Creating EventBridge rule...")

    rule_response = events.put_rule(
        Name=RULE_NAME,
        ScheduleExpression=SCHEDULE_EXPRESSION,
        State="ENABLED",
    )

    rule_arn = rule_response["RuleArn"]
    print(f"Rule created: {rule_arn}")

    events.put_targets(
        Rule=RULE_NAME,
        Targets=[
            {
                "Id": "LowOccupancyLambdaTarget",
                "Arn": f"arn:aws:lambda:us-east-1:414333503877:function:{LAMBDA_FUNCTION_NAME}"
            }
        ]
    )

    try:
        lambda_client.add_permission(
            FunctionName=LAMBDA_FUNCTION_NAME,
            StatementId="EventBridgeInvokePermission",
            Action="lambda:InvokeFunction",
            Principal="events.amazonaws.com",
            SourceArn=rule_arn
        )
        print("Invocation permission added to Lambda.")
    except lambda_client.exceptions.ResourceConflictException:
        print("Permission already exists — skipping.")

if __name__ == "__main__":
    create_eventbridge_rule()

import boto3

sns = boto3.client("sns")

# to create a topic of sns
def create_sns_topics():
    topics = ["low-occupancy-alert", "revenue-drop-alert"]
    for topic in topics:
        response = sns.create_topic(Name=topic)
        print(f"Created topic {topic}: {response['TopicArn']}")

if __name__ == "__main__":
    create_sns_topics()
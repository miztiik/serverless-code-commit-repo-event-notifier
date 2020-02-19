import os
import json
import boto3
import dateutil.parser
import logging
from botocore.vendored import requests

# Initialize Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def set_global_vars():
    """
    Set the Global Variables
    If User provides different values, override defaults

    This function returns the AWS account number

    :return: global_vars
    :rtype: dict
    """
    global_vars = {'status': False}
    try:
        global_vars['Owner'] = "Mystique"
        global_vars['Environment'] = "Prod"
        global_vars['tag_name'] = "serverless-code-commit-repo-event-notifier"
        global_vars['slack_webhook_url'] = os.environ.get("slack_webhook_url")
        global_vars['sns_topic_arn'] = os.environ.get("sns_topic_arn")
        global_vars['status'] = True
    except Exception as err:
        logger.error(f"Unable to set global variables. ERROR:{err}")
        global_vars['error_message'] = str(err)
    return global_vars


def post_to_slack(webhook_url, slack_data, record):
    """
    Post message to given slack channel/url

    :param webhook_url: The lambda event
    :param type: str
    :param slack_data: A json containing slack performatted text data
    :param type: json

    :return: key_exists Returns True, If key exists, False If Not.
    :rtype: bool
    """
    resp = {'status': False}
    slack_msg = {}
    slack_msg["text"] = ''
    slack_msg["attachments"] = []
    tmp = {}

    tmp["fallback"] = "Event Detected."
    tmp["color"] = record.get("color")
    tmp["pretext"] = f"CodeCommit Event detected in `{record.get('awsRegion')}` in Repo:`{record.get('eventSourceARN').split(':')[-1]}`"
    tmp["author_name"] = "Serverless-Repo-Monitor"
    tmp["author_link"] = "https://github.com/miztiik/serverless-code-commit-repo-event-notifier"
    tmp["author_icon"] = "https://avatars1.githubusercontent.com/u/12252564?s=400&u=20375d438d970cb22cc4deda79c1f35c3099f760&v=4"
    tmp["title"] = f"Repo Event: {record.get('eventName')}"
    tmp["title_link"] = f"https://console.aws.amazon.com/codesuite/codecommit/repositories/{record.get('eventSourceARN').split(':')[-1]}/browse?region={record.get('awsRegion')}"
    tmp["fields"] = [
        {
            "title": "Repo Name",
            "value": f"`{slack_data.get('repo_metadata').get('repositoryName')}`",
            "short": True
        },
        {
            "title": "Repo Default Branch",
            "value": f"`{slack_data.get('repo_metadata').get('defaultBranch')}`",
            "short": True
        },
        {
            "title": "Triggered-By",
            "value": f"`{record.get('userIdentityARN')}`",
            "short": True
        },
        {
            "title": "Trigger Name",
            "value": f"`{record.get('eventTriggerName')}`",
            "short": True
        }
    ]
    tmp["footer"] = "AWS CodeCommit"
    tmp["footer_icon"] = "https://raw.githubusercontent.com/miztiik/serverless-code-commit-repo-event-notifier/master/images/aws-code-commit-logo.png"
    tmp["ts"] = int(dateutil.parser.parse(record.get('eventTime')).timestamp())
    tmp["mrkdwn_in"] = ["pretext", "text", "fields"]
    slack_msg["attachments"].append(tmp)
    logger.info(json.dumps(slack_msg, indent=4, sort_keys=True))

    # slack_payload = {'text':json.dumps(i)}
    try:
        p_resp = requests.post(webhook_url, data=json.dumps(
            slack_msg), headers={'Content-Type': 'application/json'})
        resp["status"] = True
    except Exception as e:
        logger.error(f"ERROR:{str(e)}")
        resp["error_message"] = f"ERROR:{str(e)}"

    if p_resp.status_code < 400:
        logger.info(
            f"INFO: Message posted successfully. Response:{p_resp.text}")
        resp["error_message"] = f"{p_resp.text}"
    elif p_resp.status_code < 500:
        logger.error(f"Unable to post to slack. ERROR: {p_resp.text}")
        resp["error_message"] = f"{p_resp.text}"
    else:
        logger.error(f"Unable to post to slack. ERROR: {p_resp.text}")
        resp["error_message"] = f"{p_resp.text}"
    return resp


def lambda_handler(event, context):
    # Can Override the global variables using Lambda Environment Parameters
    logger.info(f"event:  {str(event)}")
    global_vars = set_global_vars()
    resp = {"status": False, "error_message": ''}

    if not global_vars.get('status'):
        resp["error_message"] = global_vars.get('error_message')
        return resp

    # Log the updated references from the event
    codecommit = boto3.client('codecommit')
    references = {reference['ref']
                  for reference in event['Records'][0]['codecommit']['references']}
    logger.info(f"References:  {str(references)}")

    # Get the repository from the event and show its git clone URL
    repository = event['Records'][0]['eventSourceARN'].split(':')[5]
    try:
        response = codecommit.get_repository(repositoryName=repository)
        event['repo_metadata'] = response.get('repositoryMetadata')
        logger.info(
            f"Clone URL: {response['repositoryMetadata']['cloneUrlHttp']}")
        # Update backup status to SNS Topic
        if global_vars.get('slack_webhook_url'):
            for record in event.get("Records"):
                post_to_slack(global_vars.get(
                    'slack_webhook_url'), event, record)
        logger.info(f"slackData:  {str(event)}")

        resp['repo_data'] = response['repositoryMetadata']
        resp['status'] = True
    except Exception as err:
        logger.error(
            f"Error getting repository: {repository}. Make sure it exists and that your repository is in the same region as this function. ERROR: {str(err)}")
        resp['error_message'] = str(err)

    resp['repo_data']['creationDate'] = None
    resp['repo_data']['lastModifiedDate'] = None

    logger.info(f"resp:  {str(resp)}")

    return resp

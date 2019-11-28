from email import message_from_file
import json
import boto3
import re
import os
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

DISABLED_MESSAGE_IDS = ['AMAZON_SES_SETUP_NOTIFICATION']

def lambda_handler(event, context):

    logger.info(json.dumps(event))
    logger.debug(event.get('Records')[0].get('Sns').get('Message'))
    message = json.loads(event.get('Records')[0].get('Sns').get('Message'))
    message_id = message.get('mail').get('messageId')
    if message_id in DISABLED_MESSAGE_IDS:
        logger.info('Skip Invalid messageID. (%s)' % message_id)
        return
    notification_type = message.get('notificationType')
    destinations = message.get('mail').get('destination')
    bucket_name = message.get('receipt').get('action').get('bucketName')
    object_key = message.get('receipt').get('action').get('objectKey')

    mail_from = destinations[0] if not os.environ['MAIL_FROM'] else os.environ['MAIL_FROM']
    forward_to = os.environ['RCPT_TO'].split(",")

    # get s3 object
    s3 = boto3.client('s3')
    response = s3.get_object(
        Bucket = bucket_name,
        Key    = object_key
    )

    # change mail headers
    raw_mail = response['Body']
    msg = message_from_file(raw_mail)

    del msg['DKIM-Signature']
    del msg['To']
    del msg['From']
    del msg['Return-Path']

    msg['To'] = ", ".join(forward_to)
    msg['From'] = mail_from
    msg['Return-Path'] = mail_from

    # send mail
    ses = boto3.client('ses')
    response = ses.send_raw_email(
        Source = mail_from,
        Destinations = forward_to,
        RawMessage = {
            'Data': msg.as_string()
        }
    )
    logger.info(json.dumps(response))
    return response

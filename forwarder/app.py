import json
import boto3
import re
import os

DISABLED_MESSAGE_IDS = ['AMAZON_SES_SETUP_NOTIFICATION']

def lambda_handler(event, context):

    print(json.dumps(event))
    print(event.get('Records')[0].get('Sns').get('Message'))
    message = json.loads(event.get('Records')[0].get('Sns').get('Message'))
    message_id = message.get('mail').get('messageId')
    if message_id in DISABLED_MESSAGE_IDS:
        print('Skip Invalid messageID. (%s)' % message_id)
        return
    notification_type = message.get('notificationType')
    destinations = message.get('mail').get('destination')
    bucket_name = message.get('receipt').get('action').get('bucketName')
    object_key = message.get('receipt').get('action').get('objectKey')

    mail_from = destinations[0] if not os.environ['MAIL_FROM'] else os.environ['MAIL_FROM']
    forward_to = os.environ['RCPT_TO'].split(",")

    # get s3 object
    try:
        s3 = boto3.client('s3')
        response = s3.get_object(
            Bucket = bucket_name,
            Key    = object_key
        )
    except Exception as e:
        raise e

    # change mail headers
    try:
        replaced_message = response['Body'].read().decode('utf-8')
        replaced_message = re.sub("\nTo: .+?\n", "\nTo: %s\n" % ", ".join(forward_to), replaced_message, 1)
        replaced_message = re.sub("\nFrom: .+?\n", "\nFrom: %s\n" % mail_from, replaced_message, 1)
        replaced_message = re.sub("^Return-Path: .+?\n", "Return-Path: %s\n" % mail_from, replaced_message, 1)
    except Exception as e:
        raise e

    # send mail
    try:
        ses = boto3.client('ses')
        response = ses.send_raw_email(
            Source = mail_from,
            Destinations = forward_to,
            RawMessage={
                'Data': replaced_message
            }
        )
        print(json.dumps(response))
        return response
    except Exception as e:
        raise e

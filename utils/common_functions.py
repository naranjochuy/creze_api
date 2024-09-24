import boto3
import json
from django.conf import settings
from botocore.exceptions import ClientError


def send_email():
    if settings.ENVIRONMENT == 'prod':
        try:
            client = boto3.client('lambda', region_name='us-east-1')
            payload = {
                'from_email': 'jnaranjo@rmmlex.com',
                'to_address': 'naranjo.chuy@gmail.com'
            }
            client.invoke(
                FunctionName='send_email_creze',
                InvocationType='Event',
                Payload=json.dumps(payload)
            )
        except Exception as e:
            print(f"Error al consumir lambda: {e}")


def get_secret():
    if settings.ENVIRONMENT == 'dev':
        return {}

    client = boto3.client("secretsmanager", region_name="us-east-1")

    try:
        get_secret_value_response = client.get_secret_value(SecretId="creze")
    except ClientError as e:
        raise e
    else:
        secret = get_secret_value_response.get("SecretString", None)
        if secret:
            return json.loads(secret)
        else:
            raise ValueError("No hay datos o no tienen el formato correcto")

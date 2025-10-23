import random
import string
import re
import boto3
import json

def generate_strong_value():
    """Generate a strong random string (16 chars, mixed letters, digits, special)."""
    upper = string.ascii_uppercase
    lower = string.ascii_lowercase
    digits = string.digits
    special = "@#$%^&*_-+="
    all_chars = upper + lower + digits + special

    while True:
        value = ''.join(random.choice(all_chars) for _ in range(16))
        categories = sum([
            any(c in upper for c in value),
            any(c in lower for c in value),
            any(c in digits for c in value),
            any(c in special for c in value)
        ])
        if categories < 3:
            continue
        if re.search(r'(.)\1\1', value):
            continue
        return value

def lambda_handler(event, context):
    client = boto3.client('secretsmanager')
    secret_id = event['SecretId']
    token = event['ClientRequestToken']

    # List of keys to exclude from rotation
    exclude_keys = ["apiKey", "serviceToken"]  # Add key names here

    # Get current secret value
    current_secret = client.get_secret_value(SecretId=secret_id)
    secret_dict = json.loads(current_secret['SecretString'])

    # Update all key values except those in exclude_keys
    for key in secret_dict:
        if key not in exclude_keys:
            secret_dict[key] = generate_strong_value()

    # Store updated secret in AWSPENDING
    client.put_secret_value(
        SecretId=secret_id,
        ClientRequestToken=token,
        SecretString=json.dumps(secret_dict)
    )

    return {
        "status": "success",
        "message": f"Updated values for {len(secret_dict) - len(exclude_keys)} keys successfully. Excluded: {exclude_keys}"
    }  
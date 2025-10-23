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

def rotate_secret(secret_name, exclude_keys):
    client = boto3.client('secretsmanager')
    current = client.get_secret_value(SecretId=secret_name)
    secret_data = json.loads(current['SecretString'])

    updated = 0
    for key in secret_data:
        if key not in exclude_keys:
            secret_data[key] = generate_strong_value()
            updated += 1

    client.put_secret_value(
        SecretId=secret_name,
        SecretString=json.dumps(secret_data)
    )

    return {"secret": secret_name, "updated_keys": updated, "excluded": exclude_keys}

def lambda_handler(event, context):
    secrets = event.get('secrets', [])
    if not secrets:
        return {"status": "error", "message": "No secrets provided"}

    results = []
    for s in secrets:
        name = s.get('name')
        exclude = s.get('exclude', [])
        try:
            result = rotate_secret(name, exclude)
            results.append(result)
        except Exception as e:
            results.append({"secret": name, "error": str(e)})

    return {"status": "completed", "results": results}
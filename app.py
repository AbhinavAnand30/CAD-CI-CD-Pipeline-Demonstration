import json

def add(a, b):
    return a + b

def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Hello from CADDemoFunction"
        })
    }
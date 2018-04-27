import boto3
import json
from botocore.vendored import requests
import base64

GOOGLE_CLOUD_VISION_API_URL = 'https://vision.googleapis.com/v1/images:annotate?key='
s3 = boto3.resource('s3')

def goog_cloud_vision (event, context):
    image =get_object_body(event['bucket'], event['key'])
    encoded_img = base64.b64encode(image).decode('utf-8') 
    TxtKey = "OCR-"+event['key']+".txt"
    api_url = GOOGLE_CLOUD_VISION_API_URL + "API_KEY"
    req_body = json.dumps({
        'requests': [{
            'image': {
                'content': encoded_img
            },
            'features': [{
                'type': 'TEXT_DETECTION',
                'maxResults': 10,
            }]
        }]
    })
    res = requests.post(api_url, data=req_body)

    text = (res.json()['responses'][0]['fullTextAnnotation']['text'])
	#text1 = (res.json()["responses"][0]["textAnnotations"][0].get("description", None))
    text = text.replace('\r', '').replace('\n', '')
    print (text)
    s3.Bucket("ist440grp2ocr").put_object(Key=TxtKey, Body=text, ACL='public-read', ContentType='txt/html')
    output = {
        "bucket": "ist440grp2ocr",
        "key": TxtKey
    }
    return output
def get_object_body(bucket, key):
    """
    Get object body in S3
    :param bucket: bucket name
    :param key: object key
    :return: binary strings
    """
    obj = s3.Object(bucket, key)
    response = obj.get()
    body = response['Body'].read()
    return body
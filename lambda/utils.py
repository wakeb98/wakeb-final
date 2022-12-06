import logging
import os
import boto3
from botocore.exceptions import ClientError
import numpy as np
import pandas as pd
import requests
from difflib import SequenceMatcher

def create_presigned_url(object_name):
    """Generate a presigned URL to share an S3 object with a capped expiration of 60 seconds

    :param object_name: string
    :return: Presigned URL as string. If error, returns None.
    """
    s3_client = boto3.client('s3',
                             region_name=os.environ.get('S3_PERSISTENCE_REGION'),
                             config=boto3.session.Config(signature_version='s3v4',s3={'addressing_style': 'path'}))
    try:
        bucket_name = os.environ.get('S3_PERSISTENCE_BUCKET')
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=60*1)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response
    
def check_similarity(word, list_of_word):
    listk = []
    for i in list_of_word:
        s = SequenceMatcher(None, word, i)
        listk.append(s.ratio())
    return np.argmax(listk)   
    
    
def sync_questions(API_URL, API_TOKEN, question):
    res = requests.post(f'{API_URL}/api/questions/store', headers={
        'Accept': 'application/json',
        'X-Authorization': API_TOKEN
    }, json = question)

    return res.status_code
    
def sync_readings(API_URL, API_TOKEN):
    response = requests.get(API_URL, headers={
        'Accept': 'application/json',
        'X-Authorization': API_TOKEN
    })
    #if type(response.json()['Al-Jubail']) != None:
    readings = response.json()
    sheet = pd.DataFrame(readings)
    
    #return readings
    return sheet    
    
def f(s):
    return "" if not s else f(s[2:]) + s[:2]    
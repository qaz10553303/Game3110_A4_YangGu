import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('RemoteSettings')

def lambda_handler(event, context):
    if event['httpMethod'] == 'GET':
        if 'GameName' in event['body']:
            GameName= json.loads(event['body'])['GameName']
            scanFilter=Attr('GameName').eq(GameName)
            if 'Key' in event['body']:
                Key= json.loads(event['body'])['Key']
                scanFilter=scanFilter&Attr('Variable').eq(Key)
            response = table.scan(
                FilterExpression=scanFilter
            )
            return debug_log(json.dumps(response['Items']))
        else:return debug_log('Bad Request:Missing GameName!')
    elif event['httpMethod'] == 'PUT':
        body=json.loads(event['body'])
        if 'GameName' in body:
            if 'Key' in body:
                if 'Value' in body:
                    gameName=body['GameName']
                    key=body['Key']
                    value=body['Value']
                    table.put_item(
                        Item={
                                'GameName':gameName,
                                'Variable':key,
                                'Value':value
                            }
                    )
                    user=table.get_item(
                        Key={
                            
                                'GameName':gameName,
                                'Variable':key
                            }
                    )
                    userItem=user['Item']
                    return debug_log('Settings Updated!\n'+json.dumps(userItem))
                else:return debug_log('Bad Request:Missing Value!')    
            else:return debug_log('Bad Request:Missing Key!')
        else:return debug_log('Bad Request:Missing GameName!')
    else:return debug_log('Bad Request:Not Supported Method!')
        
        
        
def debug_log(log) :
    return{
        'statusCode': 200,
        'body': log
    }

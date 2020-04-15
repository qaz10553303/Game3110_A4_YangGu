import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AssignmentWar')

def lambda_handler(event, context):
    # TODO implement
    if'body' in event:
        if event['httpMethod'] == 'GET':
            if 'UserName' in event['body']:
                if 'GameName' in event['body']:
                    if json.loads(event['body'])['GameName']=='AssignmentWar':
                        user=table.get_item(Key={'UserName':json.loads(event['body'])['UserName']})
                        if 'Item' in user:return debug_log(json.dumps(user['Item']))
                        else:return debug_log('Bad Request:No Such User!')
                    else:return debug_log('Bad Request:Wrong GameName!')
                else:return debug_log('Bad Request:Missing GameName!')
            else:return debug_log('Bad Request:Missing UserName!')
        elif event['httpMethod'] == 'PUT':
            if 'UserName' in event['body'] and 'Score' in event['body']:
                if 'GameName' in event['body']:
                    if json.loads(event['body'])['GameName']=='AssignmentWar':
                        try:
                            int(json.loads(event['body'])['Score'])
                        except ValueError:
                            return debug_log('Bad Request:Score Type Must Be Int!')
                        else:
                            table.put_item(
                                Item={
                                        'UserName':json.loads(event['body'])['UserName'],
                                        'Score':json.loads(event['body'])['Score']
                                    }
                            )
                            user=table.get_item(
                                Key={
                                        'UserName':json.loads(event['body'])['UserName'],
                                    }
                            )
                            user['Item']['Score']=str(user['Item']['Score'])
                            return debug_log('Score Updated!\n'+json.dumps(user['Item']))
                    else:return debug_log('Bad Request:Wrong GameName!')
                else:return debug_log('Bad Request:Missing GameName!')
            else:return debug_log('Bad Request:Missing UserName or Score!')
        else:return debug_log('Bad Request:Not Supported Method!')
    else:return debug_log('Bad Request:Missing body!')

    
def debug_log(log) :
    return{
        'statusCode': 200,
        'body': log
    }

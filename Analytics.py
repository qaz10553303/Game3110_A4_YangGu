import json
import boto3
import datetime 
import time
from boto3.dynamodb.conditions import Key, Attr
from decimal import *

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Analytics')

def lambda_handler(event, context):
    if event['httpMethod'] == 'GET':
        currentTime=time.time()
        currentTime_d = Decimal(currentTime).quantize(Decimal('0.001'),rounding=ROUND_DOWN)
        scanFilterCount=0
        body=json.loads(event['body'])
        if 'UserName' in event['body']:
            UserName=body['UserName']
            if scanFilterCount==0:
                scanFilter=Attr('UserName').eq(UserName)
                scanFilterCount+=1
            else:
                scanFilter=scanFilter&Attr('UserName').eq(UserName)
                scanFilterCount+=1
        if 'GameName' in event['body']:
            GameName=body['GameName']
            if scanFilterCount==0:
                scanFilter=Attr('GameName').eq(GameName)
                scanFilterCount+=1
            else:
                scanFilter=scanFilter&Attr('GameName').eq(GameName)
                scanFilterCount+=1
        if 'TimeStart' in event['body']:
            TimeStart=body['TimeStart']
            if len(TimeStart)==12:
                timeArray=time.strptime(TimeStart,"%Y%m%d%H%M")
                TimeStart_d=time.mktime(timeArray)+14400
            else:return debug_log('Bad Request:You Have To Use Specific Time Format:%Y%m%d%H%M\ne.g."202004151128"')
            if scanFilterCount==0:
                scanFilter=Attr('TimeStamp').gte(Decimal(TimeStart_d))
                scanFilterCount+=1
            else:
                scanFilter=scanFilter&Attr('TimeStamp').gte(Decimal(TimeStart_d))
                scanFilterCount+=1
        if 'TimeEnd' in event['body']:
            TimeEnd=body['TimeEnd']
            if len(TimeEnd)==12:
                timeArray=time.strptime(TimeEnd,"%Y%m%d%H%M")
                TimeEnd_d=time.mktime(timeArray)+14400
            else:return debug_log('Bad Request:You Have To Use Specific Time Format:%Y%m%d%H%M\ne.g."202004151128"')
            if scanFilterCount==0:
                scanFilter=Attr('TimeStamp').lte(Decimal(TimeEnd_d))
                scanFilterCount+=1
            else:
                scanFilter=scanFilter&Attr('TimeStamp').lte(Decimal(TimeEnd_d))
                scanFilterCount+=1
        if scanFilterCount==0:
            return debug_log('Bad Request:You Have To Have ONE Filter At Least!\nFilter List:"UserName""GameName""TimeStart""TimeEnd"')
        else:
            response = table.scan(
                FilterExpression=scanFilter
            )

            if 'Items' in response:
                # response['Items']['TimeStamp']=str(response['Items']['TimeStamp'])
                # return debug_log('Successful!\n'+json.dumps(response['Items']))
                for index in range(len(response['Items'])):
                    response['Items'][index]['TimeStamp']=str(response['Items'][index]['TimeStamp'])
                return debug_log(str(response['Count'])+' Items Found!\n'+json.dumps(response['Items']))
            else:return debug_log('Bad Request:Unexpected Error!')
    
    elif event['httpMethod'] == 'POST':
        # currentTime= datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        # currentTime=time.mktime(time.strptime(currentTime,'%Y%m%d%H%M%S'))
        currentTime=time.time()
        currentTime_d = Decimal(currentTime).quantize(Decimal('0.001'),rounding=ROUND_DOWN)
        if 'UserName' in event['body']:
            if 'GameName' in event['body']:
                if 'EventType' in event['body']:
                    if 'EventDetail' in event['body']:
                        table.put_item(
                            Item={
                                    'UserName':json.loads(event['body'])['UserName'],
                                    'TimeStamp':currentTime_d,
                                    'GameName':json.loads(event['body'])['GameName'],
                                    'EventType':json.loads(event['body'])['EventType'],
                                    'EventDetail':json.loads(event['body'])['EventDetail']
                                }
                        )
                        user=table.get_item(
                            Key={
                                    'TimeStamp':currentTime_d,
                                    'UserName':json.loads(event['body'])['UserName']
                                }
                            )
                        if 'Item' in user:
                            user['Item']['TimeStamp']=str(user['Item']['TimeStamp'])
                            return debug_log('Successful!\n'+json.dumps(user['Item']))
                        else:return debug_log('Bad Request:Unexpected Error!')
                    else:return debug_log('Bad Request:Missing EventDetail!')
                else:return debug_log('Bad Request:Missing EventType!')
            else:return debug_log('Bad Request:Missing GameName!')   
        else:return debug_log('Bad Request:Missing UserName!')
        # return debug_log(currentTime)
        # else:return debug_log('Bad Request:Missing Data!')    
    else:return debug_log('Bad Request:Not Supported Method!')
    
    
def debug_log(log) :
    return{
        'statusCode': 200,
        'body': log
    }

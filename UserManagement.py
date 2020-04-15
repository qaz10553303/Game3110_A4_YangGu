import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Account')

def lambda_handler(event, context):

    #  table = dynamodb.Table('Account')

    if 'Operation' in event['headers']:
        if'body' in event:
            if event['httpMethod'] == 'GET':
                if 'UserName' in event['body']:
                    user=getUserById(json.loads(event['body'])['UserName'])
                    return debug_log(json.dumps(user))
            elif event['httpMethod'] == 'PUT':   #User Login/Logout & update#
                if 'UserName' in event['body'] and 'UserPassword' in event['body']:
                    myName=json.loads(event['body'])['UserName']
                    myPassword=json.loads(event['body'])['UserPassword']
                    if event['headers']['Operation']=='Login':
                        # return debug_log('now login')
                        myStatus='Online'
                        return updateUserStatus(myName,myPassword,myStatus)
                    elif event['headers']['Operation']=='Logout':
                        # return debug_log('now logout')
                        myStatus='Offline'
                        return updateUserStatus(myName,myPassword,myStatus)
                    elif event['headers']['Operation']=='Update':
                        return updateUserInfo(myName,myPassword)
                    else:return debug_log('Bad Request:Operation needs to be Login,Logout or Update!')
                else: return debug_log('Bad Request:Missing ID or password!')
            elif event['httpMethod'] == 'POST':   #User Register#
                if 'UserName' in event['body'] and 'UserPassword' in event['body']:
                    myName=json.loads(event['body'])['UserName']
                    myPassword=json.loads(event['body'])['UserPassword']
                    return registerUser(myName,myPassword)
                else: return debug_log('Bad Request:Missing ID or password!')
            else:return debug_log('Bad Request:Not Supported Method!')
        else:return debug_log('Bad Request:Missing body!')
    else:return debug_log('Bad Request:Missing operation!')


def registerUser(userId,password):
    user=table.get_item(Key={'UserName':userId})
    if 'Item' in user:return debug_log('Bad Request:User Already Exists!')
    else: 
        table.put_item(
            Item={
                    'UserName':userId,
                    'UserPassword':password,
                }
        )
        return debug_log('Registration Complete!')

def getUserById(userId):
    user=table.get_item(Key={'UserName':userId})
    if 'Item' in user:return user['Item']
    else:return debug_log('Bad Request:No Such User!')

def updateUserInfo(userId,password):
    user=table.get_item(Key={'UserName':userId})
    if 'Item' in user:
        table.update_item(
            Key={
                'UserName': userId
            },
            UpdateExpression='SET UserPassword = :val',
            ExpressionAttributeValues={
                ':val': password
            }
        )
        user=table.get_item(Key={'UserName':userId})
        userItem=user['Item']
        return debug_log('User Update Successful!\n'+json.dumps(userItem))
    else:return debug_log('Bad Request:No Such User!')
    
def updateUserStatus(userId,password,myStatus):
    user=table.get_item(Key={'UserName':userId})
    if 'Item' in user:
        userItem=user['Item']
        if userItem['UserName']==userId and userItem['UserPassword']==password:
            table.update_item(
                Key={
                    'UserName': userId
                },
                UpdateExpression='SET UserStatus = :val',
                ExpressionAttributeValues={
                    ':val': myStatus
                }
            )
            return debug_log(userId+' Is Now '+myStatus)
        else:debug_log('Bad Request:Wrong ID Or Password!')
    else:return debug_log('Bad Request:No Such User!')



def debug_log(log) :
    return{
        'statusCode': 200,
        'body': log
    }

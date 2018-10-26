import os
import boto3
import hashlib

from chalice import Chalice, Response, BadRequestError
from chalice import NotFoundError

app = Chalice(app_name='demo')
app.debug = True


DDB = boto3.client('dynamodb')

@app.route('/', methods=['POST'])
def shorten():
	url = app.current_request.json_body.get('url', '');
	if not url:
		raise BadRequestError("Missing URL")
	digest = hashlib.md5(url.encode('utf-8')).hexdigest()[:6]
	DDB.put_item(
		TableName=os.environ['APP_TABLE_NAME'],
		Item={'identifier': {'S': digest},
			'url': {'S': url}})

	return {'shortened': digest}

@app.route('/{identifier}', methods=['GET'])
def retrieve(identifier):
	try:
		record = DDB.get_item(Key={'identifier': {'S': identifier}},
				TableName=os.environ['APP_TABLE_NAME'])['Item']['url']['S']
		
	except Exception as e:
		return Response(
			status_code=404,
			body=identifier + ' not found')

	return Response(
	status_code=301,
	headers={'location': record},
	body='')

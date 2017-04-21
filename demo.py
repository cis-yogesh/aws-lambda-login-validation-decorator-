def authenticate(func):
    """
    authentication of the api in aws lambda decorator
    @authenticate  as decorator in your lambda and get a requrester params in lambda.
    """
    @functools.wraps(func)
    def call_func(event, context, **other_args):

        user = context.identity.cognito_identity_id
        if not user:
            if 'requestContext' in event:
                other_args['user'] = user = event['requestContext']['identity']['cognitoIdentityId']

        if not user:
            raise Exception('User is not athenticated by cognito Identity Pool')

        response = func(event, context, **other_args)
        return response
    return call_func


def lambda_wrapper(func):
    @functools.wraps(func)
    def call_func(event, context, **other_args):

        try:
            if not other_args.get('dynamodb'):
                dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
                other_args['dynamodb'] = dynamodb

            query_body = event.get("body", False)
            if query_body:
                other_args['query_body'] = json.loads(query_body)
            
            query_parameters = event.get("queryStringParameters", {})
            if query_parameters:
                other_args['query_parameters'] = query_parameters

            response = func(event, context, **other_args)

        except Exception, e:
            logger.error("error: {}".format(str(e)))
            return {
                "statusCode": 500,
                "body": "Error: {}".format(str(e))
            }

        else:
            return {
                "statusCode": 200,
                "body": json.dumps(response, cls=DecimalEncoder)
            }

    return call_func

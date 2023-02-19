This repository contains an example for running FastAPI in Lambda using mangum, deployed through CDK.
The application logic is not particularly interesting, it only serves to demonstrate the use of these tools.

This stack uses Cognito for authentication, which I don't normally recommend,
but it's the quickest way to put some authentication around an HTTP API Gateway
on AWS.

# Pre-requisites
1. Python 3.9
2. An AWS account
3. [CDK](https://aws.amazon.com/cdk/) to deploy to AWS
4. [Docker](https://www.docker.com/), both for building the Python bundle using CDK and for running DynamoDB locally
5. [poetry](https://python-poetry.org/) for package management

# Local Development

Install all dependencies using poetry:

```shell
poetry install
```

The tests should be passing once all dependencies are installed:

```shell
pytest .
```

# Deployments

You can deploy this application to your AWS account using CDK. Before you run CDK,
export the dependencies into the `./application` folder, as the `PythonFunction`
will look for the requirements here. Make sure only the `application` dependencies
are exported:

```shell
poetry export -o application/requirements.txt --only application
```

Run CDK to deploy:

```shell
cdk deploy
```

This requires Docker to be installed on your computer, as `PythonFunction`
uses Docker for bundling the dependencies for the correct platform.


> **Warning**
>
> At the time of writing this, bundling fails on M1 Macs if the following flag is not set:
> ```shell
> export DOCKER_DEFAULT_PLATFORM=linux/amd64
> ```

# Testing the deployed application

The deployed application uses Cognito for authentication. The stack should output
the Cognito user pool and client ID. Use these to create a user and get a password
for API calls.

To create a user:

```shell
aws cognito-idp admin-create-user --user-pool-id $USER_POOL_ID --username $USER_ID
aws cognito-idp admin-set-user-password --user-pool-id $USER_POOL_ID --username $USER_ID --password $PASSWORD --permanent
```

To get a new access token:

```shell
TOKEN=aws cognito-idp admin-initiate-auth --user-pool-id $USER_POOL_ID --client-id $CLIENT_ID --auth-flow ADMIN_USER_PASSWORD_AUTH --auth-parameters "USERNAME=$USER_ID,PASSWORD=$PASSWORD" --profile eloscript | jq -r ".AuthenticationResult.AccessToken"
```

Using the access token, we can now attempt to create a new account:

```shell
# API_URL is the URL printed as CloudFormation output for the API Gateway
curl -X POST -H "Content-Type: application/json" -H "Authorization: $TOKEN" $API_URL/account
```

This will return an account ID and a balance of 0. Using the account ID, you can
execute transactions for the account:

```shell
curl -X POST -H "Content-Type: application/json" -H "Authorization: $TOKEN" -d '{"action": "deposit", "amount": 100}' $API_URL/account/$ACCOUNT_ID/transactions
```

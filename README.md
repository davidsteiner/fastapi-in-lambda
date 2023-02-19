This repository contains an example for running FastAPI in Lambda using mangum, deployed through CDK.
The application logic is not particularly interesting, it only serves to demonstrate the use of these tools.

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

To run Docker for PythonLambda on M1 chip:

```shell
export DOCKER_DEFAULT_PLATFORM=linux/amd64
```

To export dependencies:

```shell
poetry export -o application/requirements.txt --only application
```

Create a user:

```shell
aws cognito-idp admin-create-user --user-pool-id $USER_POOL_ID --username $USERNAME
aws cognito-idp admin-set-user-password --user-pool-id $USER_POOL_ID --username $USERNAME --password $PASSWORD --permanent
```

To get a password:

```shell
aws cognito-idp admin-initiate-auth --user-pool-id $USER_POOL_ID --client-id $CLIENT_ID --auth-flow ADMIN_USER_PASSWORD_AUTH --auth-parameters "USERNAME=$USERNAME,PASSWORD=$PASSWORD"
```

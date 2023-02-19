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
aws cognito-idp admin-create-user --user-pool-id $USER_POOL_ID --username $USERNAME
aws cognito-idp admin-set-user-password --user-pool-id $USER_POOL_ID --username $USERNAME --password $PASSWORD --permanent
```

To get a password:

```shell
aws cognito-idp admin-initiate-auth --user-pool-id $USER_POOL_ID --client-id $CLIENT_ID --auth-flow ADMIN_USER_PASSWORD_AUTH --auth-parameters "USERNAME=$USERNAME,PASSWORD=$PASSWORD"
```

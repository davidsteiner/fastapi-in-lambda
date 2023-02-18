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

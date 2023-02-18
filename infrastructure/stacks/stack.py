import aws_cdk.aws_lambda_python_alpha as python_lambda
from aws_cdk import CfnOutput, Stack
from aws_cdk.aws_apigatewayv2_alpha import (
    CorsHttpMethod,
    CorsPreflightOptions,
    HttpApi,
    HttpMethod,
)
from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpJwtAuthorizer
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration
from aws_cdk.aws_cognito import AuthFlow, UserPool, UserPoolClient
from aws_cdk.aws_lambda import Architecture, Function, Runtime
from constructs import Construct

ALLOWED_HEADERS = [
    "Authorization",
    "Content-Type",
]
ALLOWED_METHODS = [
    CorsHttpMethod.DELETE,
    CorsHttpMethod.GET,
    CorsHttpMethod.OPTIONS,
    CorsHttpMethod.POST,
    CorsHttpMethod.PUT,
]


class ServerlessApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str):
        super().__init__(scope, construct_id)

        handler_function = self.build_handler_function()
        http_api = self.build_http_api()
        user_pool = self.create_user_pool()
        user_pool_client = self.add_user_pool_client(user_pool)
        authorizer = self.build_authorizer(user_pool, user_pool_client)

        self.setup_lambda_integration(http_api, handler_function, authorizer)

        CfnOutput(
            self,
            "APIEndpoint",
            value=http_api.api_endpoint,
            description="The URL of the HTTP API Gateway",
        )
        CfnOutput(
            self,
            "CognitoUserPoolId",
            value=user_pool.user_pool_id,
            description="The pool ID of the Cognito user pool",
        )
        CfnOutput(
            self,
            "CognitoUserPoolClientId",
            value=user_pool_client.user_pool_client_id,
            description="The client ID of the Cognito client",
        )

    def build_handler_function(self) -> Function:
        return python_lambda.PythonFunction(
            self,
            "BackendLambda",
            entry="application/",
            index="vivaldi/app.py",
            handler="handler",
            architecture=Architecture.ARM_64,
            runtime=Runtime.PYTHON_3_9,
        )

    def build_http_api(self) -> HttpApi:
        """Build the HTTP API."""
        api = HttpApi(
            self,
            "HttpApi",
            cors_preflight=CorsPreflightOptions(
                allow_methods=ALLOWED_METHODS,
                allow_headers=ALLOWED_HEADERS,
                allow_origins=["*"],
            ),
        )

        return api

    @staticmethod
    def setup_lambda_integration(
        http_api: HttpApi,
        api_function: Function,
        authorizer: HttpJwtAuthorizer,
    ) -> None:
        """Set up the handler for Mangum/FastAPI."""
        integration = HttpLambdaIntegration(
            "LambdaIntegration",
            handler=api_function,
        )
        http_api.add_routes(
            path="/{proxy+}",
            methods=[
                HttpMethod.GET,
                HttpMethod.POST,
                HttpMethod.PUT,
                HttpMethod.PATCH,
                HttpMethod.DELETE,
            ],
            integration=integration,
            authorizer=authorizer,
        )

    def create_user_pool(self) -> UserPool:
        return UserPool(self, "UserPool", user_pool_name="vivaldi-users")

    @staticmethod
    def build_authorizer(
        user_pool: UserPool,
        user_pool_client: UserPoolClient,
    ) -> HttpJwtAuthorizer:
        """Build the request authorizer."""
        issuer = f"https://cognito-idp.{user_pool.env.region}.amazonaws.com/{user_pool.user_pool_id}"
        return HttpJwtAuthorizer(
            "JwtAuthorizer",
            jwt_issuer=issuer,
            jwt_audience=[user_pool_client.user_pool_client_id],
        )

    @staticmethod
    def add_user_pool_client(user_pool: UserPool) -> UserPoolClient:
        return user_pool.add_client(
            "app-client", auth_flows=AuthFlow(admin_user_password=True)
        )

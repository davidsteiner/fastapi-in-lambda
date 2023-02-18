from aws_cdk import App
from stacks.stack import ServerlessApiStack

app = App()

ServerlessApiStack(app, "ServerlessApiStack")

app.synth()

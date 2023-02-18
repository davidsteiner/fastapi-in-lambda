from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel

app = FastAPI(
    title="Vivaldi API",
    description="HTTP API for Vivaldi Bank",
    version="1.0",
)


class Response(BaseModel):
    name: str


@app.get("/hello")
def hello():
    return Response(name="world")


handler = Mangum(app, lifespan="off")

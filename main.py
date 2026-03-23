# main.py
from fastapi import FastAPI, Request
from conversion_management.lambda_function import lambda_handler

app = FastAPI()


@app.api_route("/{path:path}", methods=["GET", "POST"])
async def proxy(request: Request, path: str):
    body = await request.body()

    event = {
        "path": "/" + path,
        "httpMethod": request.method,
        "headers": dict(request.headers),
        "queryStringParameters": dict(request.query_params),
        "body": body.decode("utf-8") if body else None,
        "requestContext": {
            "http": {
                "method": request.method
            }
        }
    }

    response = lambda_handler(event, None)

    return response

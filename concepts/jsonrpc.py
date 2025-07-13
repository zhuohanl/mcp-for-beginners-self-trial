from fastapi import FastAPI, Body, Query, Path, Header
from pydantic import BaseModel
from typing import Literal

app = FastAPI()

# Actually should not use pydantic because the error raised does not follow
    # jsonrpc error - {"jsonrpc": "2.0"}
class JSONRPCBody(BaseModel):
    jsonrpc: Literal["2.0"]
    method: str
    params: list = []
    id: str | int = None


@app.post("/jsonrpc")
def jsonrpc_handler(body: JSONRPCBody):

    response = {"jsonrpc": "2.0"}

    if body.method == "subtract":
        params = body.params
        if not params:
            response["error"] = "params not specified"
            return response, 400
        if len(params) != 2:
            response["error"] = "Invalid parameters for subtract method"
            return response, 400

        a, b = params
        result = a - b

        response["result"] = result
        if body.id:
            response["id"] = body.id
        return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, Body
from pydantic import BaseModel

# request
# {
#     "jsonrpc": "2.0",
#     "method": "add",
#     "params": [1, 2],
#     "id": "1"
# }

# response
# {
#     "jsonrpc": "2.0",
#     "result": 3,
#     "id": "1"
# }

# error
# {
#     "jsonrpc": "2.0", 
#     "error": {
#         "code": -32600, 
#         "message": "Invalid Request"
#     }, 
#     "id": null
# }


app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/jsonrpc")
def jsonrpc(request: dict = Body(...)):

    # Validate JSON-RPC request
    if "jsonrpc" not in request or request["jsonrpc"] != "2.0" or "method" not in request:
        return {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": None}, 400
    
    # Process JSON-RPC request
    method = request.get("method")
    params = request.get("params", [])
    id = request.get("id", None)

    if method == "add":
        if len(params) != 2:
            return {"jsonrpc": "2.0", "error": {"code": -32602, "message": "Invalid params"}, "id": id}, 400
        
        a, b = params
        result = a + b
        return {"jsonrpc": "2.0", "result": result, "id": id}
    else:
        return {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": id}, 404


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
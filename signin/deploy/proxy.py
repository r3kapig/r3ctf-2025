import json
import logging
from ast import Dict, List
from contextlib import asynccontextmanager
from typing import Any, Optional
import aiohttp
from fastapi import FastAPI, Request, Response
from web3 import Web3
from eth_abi import abi
import os

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))


ALLOWED_NAMESPACES = ["web3", "eth", "net"]
DISALLOWED_METHODS = [
    "eth_sign",
    "eth_signTransaction",
    "eth_signTypedData",
    "eth_signTypedData_v3",
    "eth_signTypedData_v4",
    "eth_sendTransaction",
    "eth_sendUnsignedTransaction",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    global session
    session = aiohttp.ClientSession()

    yield

    await session.close()


app = FastAPI(lifespan=lifespan)


def solved():
    with open("/project/instance_details.json", "r") as f:
        data = json.load(f)
    chall_addr = data.get("setup")
    user_addr = data.get("player")
    (result,) = abi.decode(
        ["bool"],
        web3.eth.call(
            {
                "to": chall_addr,
                "data": web3.keccak(text="isSolved()")[:4],
                "from": user_addr,
            }
        ),
    )
    if result:
        return (
            "Challenge solved!\n"
            + "Flag: "
            + os.environ.get("FLAG", "flag{contact_admin}")
            + "\n"
        )
    return "Challenge not solved yet\n"


@app.get("/")
async def root():
    resp = "Hello!\nRPC methods are available at POST /\n\nInstance info:\n"
    if not os.path.exists("info.txt"):
        resp += "Initializing...\n"
        return Response(content=resp, media_type="text/plain")
    info = open("info.txt", "r").read()
    resp = resp + info
    if "deployed successfully" in info:
        resp = resp + "\n" + solved()
    return Response(content=resp, media_type="text/plain")


def jsonrpc_fail(id: Any, code: int, message: str) -> Dict:
    return {
        "jsonrpc": "2.0",
        "id": id,
        "error": {
            "code": code,
            "message": message,
        },
    }


def validate_request(request: Any) -> Optional[Dict]:
    if not isinstance(request, dict):
        return jsonrpc_fail(None, -32600, "expected json object")

    request_id = request.get("id")
    request_method = request.get("method")

    if request_id is None:
        return jsonrpc_fail(None, -32600, "invalid jsonrpc id")

    if not isinstance(request_method, str):
        return jsonrpc_fail(request["id"], -32600, "invalid jsonrpc method")

    if (
        request_method.split("_")[0] not in ALLOWED_NAMESPACES
        or request_method in DISALLOWED_METHODS
    ):
        return jsonrpc_fail(request["id"], -32600, "forbidden jsonrpc method")

    return None


async def proxy_request(request_id: Optional[str], body: Any) -> Optional[Any]:
    instance_host = "http://127.0.0.1:8545"

    try:
        async with session.post(instance_host, json=body) as resp:
            return await resp.json()
    except Exception as e:
        logging.error("failed to proxy anvil request to %s/%s", exc_info=e)
        return jsonrpc_fail(request_id, -32602, str(e))


@app.post("/")
async def rpc(request: Request):
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return jsonrpc_fail(None, -32600, "expected json body")

    # special handling for batch requests
    if isinstance(body, list):
        responses = []
        for idx, req in enumerate(body):
            validation_error = validate_request(req)
            responses.append(validation_error)

            if validation_error is not None:
                # neuter the request
                body[idx] = {
                    "jsonrpc": "2.0",
                    "id": idx,
                    "method": "web3_clientVersion",
                }

        upstream_responses = await proxy_request(None, body)

        for idx in range(len(responses)):
            if responses[idx] is None:
                if isinstance(upstream_responses, List):
                    responses[idx] = upstream_responses[idx]
                else:
                    responses[idx] = upstream_responses

        return responses

    validation_resp = validate_request(body)
    if validation_resp is not None:
        return validation_resp

    return await proxy_request(body["id"], body)

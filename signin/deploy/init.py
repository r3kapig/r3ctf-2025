import os
import subprocess
from ast import Dict
import requests
import time
import random
import json
import web3


RANDOM_DEPLOYER_PK = "0x" + random.randbytes(32).hex()
DEPLOYER = web3.Account.from_key(RANDOM_DEPLOYER_PK).address
INITIAL_BALANCE = 1000 * 10**18


def fill_anvil_args(args: Dict):
    if "accounts" not in args:
        args["accounts"] = "1"
    if "balance" not in args:
        if INITIAL_BALANCE is not None:
            args["balance"] = str(INITIAL_BALANCE // 10**18)
    return args


def run_anvil(args: Dict):
    cmd = ["anvil"]
    args = fill_anvil_args(args)
    for key, value in args.items():
        cmd.append(f"--{key}")
        cmd.append(value)
    subprocess.Popen(cmd)


def test_anvil():
    try:
        r = requests.post(
            "http://127.0.0.1:8545",
            json={
                "jsonrpc": "2.0",
                "method": "web3_clientVersion",
                "params": [],
                "id": 1,
            },
        )
    except Exception as e:
        print(f"Error connecting to anvil: {e}")
        return False
    return r.status_code == 200


def deploy_contract(logfile):
    global chall_addr
    print(f"[DEBUG] deployer address: {DEPLOYER}, private key: {RANDOM_DEPLOYER_PK}")
    proc = subprocess.Popen(
        [
            "cast",
            "send",
            DEPLOYER,
            "--value",
            str(INITIAL_BALANCE - 10**17),
            "--private-key",
            "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
            "--rpc-url",
            "http://127.0.0.1:8545",
        ]
    )
    stdout, stderr = proc.communicate()
    if stderr:
        print("Error funding deployer account, please contact admin", file=logfile)
        return

    curr_env = os.environ.copy()
    proc = subprocess.Popen(
        [
            "forge",
            "script",
            "--rpc-url",
            "http://127.0.0.1:8545",
            "--out",
            "/artifacts/out",
            "--cache-path",
            "/artifacts/cache",
            "--broadcast",
            "--private-key",
            RANDOM_DEPLOYER_PK,
            "script/Deploy.s.sol:Deploy",
        ],
        env=curr_env,
        cwd="/project",
        text=True,
        encoding="utf8",
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
    print("stdout: ", stdout)
    print("stderr: ", stderr)
    if stderr:
        print("Error deploying contract, please contact admin", file=logfile)
    with open("/project/instance_details.json", "r") as f:
        data = json.load(f)
    print("Challenge contract deployed at address: " + data.get("setup"), file=logfile)
    print("Your private key is: " + data.get("player_pk"), file=logfile)
    print("Your address is: " + data.get("player"), file=logfile)
    print("Contract deployed successfully", file=logfile)
    logfile.flush()
    chall_addr = data.get("setup")


def main():
    f = open("info.txt", "w")
    print("Running anvil...", file=f)
    f.flush()
    run_anvil({})
    while not test_anvil():
        time.sleep(1)
        pass
    print("Anvil is running", file=f)
    print("Deploying contract...", file=f)
    f.flush()
    deploy_contract(f)
    f.close()
    return


main()

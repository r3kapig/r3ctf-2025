import os
import subprocess
from ast import Dict, List
from typing import Any, Optional
import requests
from web3 import Web3
from eth_abi import abi
import sys
import time
import datetime


MNEUMONIC = "refuse special carry exchange usual flush life agent dune eager unlock alarm"
user_sk = "0x1c207c3a1fb67290046586a731b44ca2937b39eb116813ee153ba16c63e05d45"
user_addr = "0xF85432cea25949e96fa2107900E2712523386856"
BLOCKTIME = None

admin_sk = "0xacbc52c90d06f2652f81911432a66dc86511e13d56a4ff858bfbf6be8a0c60ea"
admin_addr = "0x19e5748694c91B9E8b555C4E91a8802C23db5fF4"
chall_addr = None


def fill_anvil_args(args: Dict):
    if not "accounts" in args:
        args["accounts"] = "2"
    if not "balance" in args:
        args["balance"] = "1000"
    if not "block-time" in args:
        if BLOCKTIME is not None:
            args["block-time"] = str(BLOCKTIME)
    if not "mnemonic" in args:
        args["mnemonic"] = MNEUMONIC
    args["hardfork"] = "prague"
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
        r = requests.post("http://127.0.0.1:8545", json={
                          "jsonrpc": "2.0", "method": "web3_clientVersion", "params": [], "id": 1})
    except:
        return False
    return r.status_code == 200


def deploy_contract(logfile):
    global chall_addr
    # run forge script Deploy.s.sol
    curr_env = os.environ.copy()
    proc = subprocess.Popen(["forge", "script", "--rpc-url", "http://127.0.0.1:8545", "--out", "/artifacts/out", "--cache-path", "/artifacts/cache", "--broadcast", "--unlocked", "--sender", "0x0000000000000000000000000000000000000000", "script/Deploy.s.sol:Deploy"],
                            env={"MNEMONIC": MNEUMONIC, "OUTPUT_FILE": "/deploy.txt"} | curr_env, cwd="/project", text=True, encoding="utf8", stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    print(stdout)
    #debug use stdout directly
    # proc = subprocess.Popen(["forge", "script", "--rpc-url", "http://127.0.0.1:8545", "--out", "/artifacts/out", "--cache-path", "/artifacts/cache", "--broadcast", "--unlocked", "--sender", "0x0000000000000000000000000000000000000000", "script/Deploy.s.sol:Deploy"],
                            # env={"MNEMONIC": MNEUMONIC, "OUTPUT_FILE": "/deploy.txt"} | curr_env, cwd="/project", text=True, encoding="utf8")

    print(stderr)
    if stderr:
        print("Error deploying contract, please contact admin", file=logfile)
    
    chall=open("/deploy.txt", "r").read()
    print("Challenge contract deployed at address: " + chall, file=logfile)
    print("Your private key is: " + user_sk, file=logfile)
    print("Your address is: " + user_addr, file=logfile)
    print("Contract deployed successfully", file=logfile)
    logfile.flush()

    #write to user.txt
    f = open("user.txt", "w")
    f.write(user_addr)
    f.close()

    chall_addr = chall.strip()


def main():
    f = open("info.txt", "w")
    print("Running anvil", file=f)
    f.flush()
    run_anvil({})
    while not test_anvil():
        time.sleep(1)
        pass
    print("Anvil is running", file=f)
    print("Deploying contract", file=f)
    f.flush()
    deploy_contract(f)

    print("Server will check the queue every 10 seconds", file=f)
    f.close()
    return


main()

time.sleep(10)

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

(arena,) = abi.decode(
    ["address"],
    web3.eth.call(
        {
            "to": chall_addr,
            "data": web3.keccak(text="arena()")[:4],
            "from": admin_addr
        }
    ),
)

arena = Web3.to_checksum_address(arena)

f = open("info.txt", "a")

def check_queue():
    (length,) = abi.decode(
        ["uint256"],
        web3.eth.call(
            {
                "to": arena,
                "data": web3.keccak(text="getBattleCount()")[:4],
                "from": admin_addr
            }
        ),
    )
    if length == 0:
        return
    print(datetime.datetime.now(), "Found", length, "battles in stack", file=f)
    f.flush()
    for i in range(length):
        tx = web3.eth.send_transaction({
            "to": arena,
            "from": admin_addr,
            "data": web3.keccak(text="processBattle(uint256)")[:4]+os.urandom(32)
        })
        print(datetime.datetime.now(), "Processed battle, tx hash:", tx.hex(), file=f)
        f.flush()

while True:
    try:
        check_queue()
    except Exception as e:
        print("Error checking stack:", e, file=sys.stderr)
        print(datetime.datetime.now(), "Error checking stack", file=f)
        f.flush()
    time.sleep(10)
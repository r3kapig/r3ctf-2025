#!/bin/bash
export ETH_RPC_URL=#
export PRIVATE_KEY=#

forge script script/Deploy.s.sol:Deploy \
--rpc-url $ETH_RPC_URL \
--private-key $PRIVATE_KEY \
--broadcast
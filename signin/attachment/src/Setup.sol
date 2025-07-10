// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Vault} from "./Vault.sol";
import {LING} from "./LING.sol";

contract Setup {
    Vault public vault;
    LING public ling;
    bool public claimed;
    bool public solved;
    constructor() {
        ling = new LING(1000 ether);
        vault = new Vault(ling);
    }

    function claim() external {
        if (claimed) {
            revert("Already claimed");
        }
        claimed = true;
        ling.transfer(msg.sender, 1 ether);
    }

    function solve() external {
        ling.approve(address(vault), 999 ether);
        vault.deposit(999 ether, address(this));
        if (vault.balanceOf(address(this)) >= 500 ether) {
            revert("Challenge not solved yet");
        }
        solved = true;
    }

    function isSolved() public view returns (bool) {
        return solved;
    }
}

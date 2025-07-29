// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.28;

import "src/Arena.sol";
import "src/Boss.sol";

contract Challenge {
    Arena public immutable arena;

    constructor() payable {
        require(msg.value >= 500 ether, "Insufficient initial balance");
        arena = new Arena();

        arena.deposit{value: msg.value}();
        arena.transfer(msg.sender, msg.value - 10 ether);

        arena.createPig(1337, 196, 101);
        arena.createPig(1234, 222, 111);
        arena.createPig(1111, 233, 110);

        arena.createPig(2025, 456, 233);
        arena.createPig(1999, 567, 222);
        arena.createPig(1898, 666, 211);


        Boss boss = new Boss();
        arena.registerAdmin(address(this), address(boss));

        arena.claimPig();
        arena.claimPig();
        arena.claimPig();

        arena.transferOwnership(msg.sender);
    }

    function isSolved() external view returns (bool) {
        return address(msg.sender).balance > 500 ether;
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {IERC4626} from "@openzeppelin/contracts/interfaces/IERC4626.sol";
import {LING} from "./LING.sol";

contract Vault is Ownable, IERC4626, ERC20("LING VAULT", "vLING") {
    struct VaultAccount {
        uint256 amount;
        uint256 shares;
    }

    VaultAccount public totalAsset;
    LING ling;
    mapping(address => uint256) public borrowedAssets;
    uint256 public totalBorrowedAssets;

    constructor(LING _ling) Ownable(msg.sender) {
        ling = _ling;
    }

    function asset() external view returns (address assetTokenAddress) {
        assetTokenAddress = address(ling);
    }

    function totalAssets() public view returns (uint256 totalManagedAssets) {
        totalManagedAssets = totalAsset.amount - totalBorrowedAssets;
    }

    function convertToShares(
        uint256 assets
    ) public view returns (uint256 shares) {
        if (totalAsset.amount == 0) {
            shares = assets;
        } else {
            shares = (assets * totalAsset.shares) / totalAsset.amount;
        }
    }

    function convertToAssets(
        uint256 shares
    ) public view returns (uint256 assets) {
        if (totalAsset.shares == 0) {
            assets = shares;
        } else {
            assets = (shares * totalAsset.amount) / totalAsset.shares;
        }
    }

    function maxDeposit(
        address /* receiver */
    ) public pure returns (uint256 maxAssets) {
        return type(uint256).max;
    }

    function previewDeposit(
        uint256 assets
    ) external view returns (uint256 shares) {
        shares = convertToShares(assets);
    }

    function deposit(
        uint256 assets,
        address receiver
    ) external returns (uint256) {
        if (assets == 0) {
            revert("zero assets");
        }
        uint256 shares = convertToShares(assets);

        totalAsset.amount += assets;
        totalAsset.shares += shares;
        ling.transferFrom(msg.sender, address(this), assets);
        _mint(receiver, shares);

        emit Deposit(msg.sender, receiver, assets, shares);
        return shares;
    }

    function maxMint(
        address /* receiver */
    ) external pure returns (uint256 maxShares) {
        return type(uint256).max;
    }

    function previewMint(
        uint256 shares
    ) external view returns (uint256 assets) {
        assets = convertToAssets(shares);
    }

    function mint(
        uint256 shares,
        address receiver
    ) external returns (uint256 assets) {
        if (shares == 0) {
            revert("zero shares");
        }
        assets = convertToAssets(shares);

        totalAsset.amount += assets;
        totalAsset.shares += shares;
        ling.transferFrom(msg.sender, address(this), assets);
        _mint(receiver, shares);

        emit Deposit(msg.sender, receiver, assets, shares);
        return assets;
    }

    function maxWithdraw(
        address owner
    ) external view returns (uint256 maxAssets) {
        uint256 shares = balanceOf(owner);
        maxAssets = convertToAssets(shares);
    }

    function previewWithdraw(
        uint256 assets
    ) external view returns (uint256 shares) {
        shares = convertToShares(assets);
    }

    function withdraw(
        uint256 assets,
        address receiver,
        address owner
    ) external returns (uint256 shares) {
        if (assets == 0) {
            revert("zero assets");
        }
        shares = convertToShares(assets);
        if (shares > balanceOf(owner)) {
            revert("insufficient shares");
        }

        if (msg.sender != owner) {
            uint256 allowed = allowance(owner, msg.sender);
            if (allowed < shares) {
                revert("insufficient allowance");
            }
            _approve(owner, msg.sender, allowed - shares);
        }

        _burn(owner, shares);
        totalAsset.amount -= assets;
        totalAsset.shares -= shares;
        ling.transfer(receiver, assets);

        emit Withdraw(msg.sender, receiver, owner, assets, shares);
        return shares;
    }

    function maxRedeem(
        address owner
    ) external view returns (uint256 maxShares) {
        return balanceOf(owner);
    }

    function previewRedeem(
        uint256 shares
    ) external view returns (uint256 assets) {
        assets = convertToAssets(shares);
    }

    function redeem(
        uint256 shares,
        address receiver,
        address owner
    ) external returns (uint256 assets) {
        if (shares > balanceOf(owner)) {
            revert("insufficient shares");
        }
        assets = convertToAssets(shares);

        if (msg.sender != owner) {
            uint256 allowed = allowance(owner, msg.sender);
            if (allowed < shares) {
                revert("insufficient allowance");
            }
            _approve(owner, msg.sender, allowed - shares);
        }

        _burn(owner, shares);
        totalAsset.amount -= assets;
        totalAsset.shares -= shares;
        ling.transfer(receiver, assets);

        emit Withdraw(msg.sender, receiver, owner, assets, shares);
        return assets;
    }

    function borrowAssets(uint256 amount) external {
        if (amount == 0) {
            revert("zero amount");
        }
        if (amount > totalAssets()) {
            revert("insufficient balance");
        }
        borrowedAssets[msg.sender] += amount;
        totalBorrowedAssets += amount;
        ling.transfer(msg.sender, amount);
    }

    function repayAssets(uint256 amount) external {
        if (amount == 0) {
            revert("zero amount");
        }
        if (borrowedAssets[msg.sender] < amount) {
            revert("invalid amount");
        }
        uint256 fee = (amount * 1) / 100;
        borrowedAssets[msg.sender] -= amount;
        totalBorrowedAssets -= amount;
        totalAsset.amount += fee;
        ling.transferFrom(msg.sender, address(this), amount + fee);
    }
}

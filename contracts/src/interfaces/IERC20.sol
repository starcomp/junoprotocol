// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.19;

/// @notice Minimal ERC-20 surface used by StakingManager.
/// @dev Production MUST use OpenZeppelin's IERC20 + SafeERC20 wrappers.
interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

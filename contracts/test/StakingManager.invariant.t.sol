// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.19;

import {Test} from "forge-std/Test.sol";
import {StakingManager} from "../src/StakingManager.sol";
import {IERC20} from "../src/interfaces/IERC20.sol";
import {MockERC20} from "./mocks/MockERC20.sol";

/// @notice Bounded action surface for invariant fuzzing of StakingManager.
contract StakingHandler is Test {
    StakingManager public sm;
    MockERC20 public token;
    address[] internal actors;

    constructor(StakingManager sm_, MockERC20 token_, address[] memory actors_) {
        sm = sm_;
        token = token_;
        actors = actors_;
    }

    function _actor(uint256 seed) internal view returns (address) {
        return actors[seed % actors.length];
    }

    function stake(uint256 seed, uint256 amount) external {
        address a = _actor(seed);
        amount = bound(amount, 1, 1e24);
        token.mint(a, amount);
        vm.startPrank(a);
        token.approve(address(sm), amount);
        sm.stake(amount);
        vm.stopPrank();
    }

    function requestUnbond(uint256 seed, uint256 amount) external {
        address a = _actor(seed);
        (uint256 staked,,) = sm.positions(a);
        if (staked == 0) return;
        amount = bound(amount, 1, staked);
        vm.prank(a);
        sm.requestUnbond(amount);
    }

    function withdraw(uint256 seed) external {
        address a = _actor(seed);
        (, uint256 unbonding, uint64 readyAt) = sm.positions(a);
        if (unbonding == 0) return;
        vm.warp(uint256(readyAt) + 1);
        vm.prank(a);
        sm.withdraw();
    }

    function slash(uint256 seed, uint256 amount) external {
        address a = _actor(seed);
        (uint256 staked,,) = sm.positions(a);
        if (staked == 0) return;
        amount = bound(amount, 1, staked);
        sm.slash(a, amount, address(0xBEEF)); // handler is the slasher (set in setUp)
    }
}

/// @notice Core accounting invariants for StakingManager.
/// @dev STUB scope: covers stake/unbond/withdraw/slash. Extend with reward
///      accounting and challenger stake once those land.
contract StakingManagerInvariant is Test {
    StakingManager internal sm;
    MockERC20 internal token;
    StakingHandler internal handler;
    address[] internal actors;

    function setUp() public {
        token = new MockERC20();
        sm = new StakingManager(IERC20(address(token)), 0, 1 days);
        actors.push(address(0xA11CE));
        actors.push(address(0xB0B));
        actors.push(address(0xCA1));
        handler = new StakingHandler(sm, token, actors);
        sm.setSlasher(address(handler)); // this contract owns sm (it deployed it)
        targetContract(address(handler));
    }

    /// `totalStaked` must always equal the sum of active stake across actors.
    function invariant_totalStakedEqualsSumOfStaked() public view {
        uint256 sum;
        for (uint256 i = 0; i < actors.length; i++) {
            (uint256 staked,,) = sm.positions(actors[i]);
            sum += staked;
        }
        assertEq(sm.totalStaked(), sum);
    }

    /// The manager must always custody at least the active + unbonding stake owed.
    function invariant_managerSolvent() public view {
        uint256 owed;
        for (uint256 i = 0; i < actors.length; i++) {
            (uint256 staked, uint256 unbonding,) = sm.positions(actors[i]);
            owed += staked + unbonding;
        }
        assertGe(token.balanceOf(address(sm)), owed);
    }
}

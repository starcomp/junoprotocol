// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.19;

import {IStakingManager} from "./interfaces/IStakingManager.sol";
import {IERC20} from "./interfaces/IERC20.sol";

/// @title StakingManager
/// @notice Holds detector (and, later, challenger) collateral in $JUNO, gates the
///         attestation write path on active stake, and exposes a slasher-only
///         `slash`. This is the economic-liability spine of the protocol.
/// @dev Skeleton. Production TODOs: SafeERC20 (check transfer returns), pull-based
///      reward accounting, real burn sink (not treasury), challenger stake type,
///      OZ Ownable2Step / AccessControl, reentrancy guards. The accounting
///      invariant `totalStaked == Σ positions[*].staked` is asserted in tests.
contract StakingManager is IStakingManager {
    IERC20 public immutable token; // tJUNO (testnet faucet token)

    address public owner; // governance / Safe council (allowlist + params)
    address public slasher; // OptimisticChallenge / Slashing module
    uint256 public minWriterStake;
    uint256 public unbondingPeriod; // seconds

    struct Position {
        uint256 staked; // active, slashable
        uint256 unbonding; // requested to withdraw, not yet matured
        uint64 unbondReadyAt; // timestamp when `unbonding` becomes withdrawable
    }

    mapping(address => Position) public positions;
    mapping(address => bool) public allowlistedWriter; // detector operator (submits)
    mapping(address => bool) public allowlistedSigner; // detector signing key (k-of-n)

    /// @notice INVARIANT: equals the sum of `positions[*].staked` (active stake only).
    uint256 public totalStaked;

    error NotOwner();
    error NotSlasher();
    error ZeroAmount();
    error InsufficientStake();
    error StillUnbonding();
    error NothingUnbonding();
    error ZeroAddress();

    event Staked(address indexed writer, uint256 amount);
    event UnbondRequested(address indexed writer, uint256 amount, uint64 readyAt);
    event Withdrawn(address indexed writer, uint256 amount);
    event Slashed(address indexed writer, uint256 amount, address indexed beneficiary, uint256 burned);
    event WriterAllowlisted(address indexed writer, bool allowed);
    event SignerAllowlisted(address indexed signer, bool allowed);
    event SlasherSet(address indexed slasher);
    event OwnerSet(address indexed owner);

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    modifier onlySlasher() {
        if (msg.sender != slasher) revert NotSlasher();
        _;
    }

    constructor(IERC20 token_, uint256 minWriterStake_, uint256 unbondingPeriod_) {
        if (address(token_) == address(0)) revert ZeroAddress();
        token = token_;
        owner = msg.sender;
        minWriterStake = minWriterStake_;
        unbondingPeriod = unbondingPeriod_;
        emit OwnerSet(msg.sender);
    }

    // --------------------------- staking ----------------------------------

    function stake(uint256 amount) external {
        if (amount == 0) revert ZeroAmount();
        // TODO: SafeERC20 — must check/raise on a false return in production.
        token.transferFrom(msg.sender, address(this), amount);
        positions[msg.sender].staked += amount;
        totalStaked += amount;
        emit Staked(msg.sender, amount);
    }

    function requestUnbond(uint256 amount) external {
        if (amount == 0) revert ZeroAmount();
        Position storage p = positions[msg.sender];
        if (p.staked < amount) revert InsufficientStake();
        p.staked -= amount;
        totalStaked -= amount;
        p.unbonding += amount;
        p.unbondReadyAt = uint64(block.timestamp) + uint64(unbondingPeriod);
        emit UnbondRequested(msg.sender, amount, p.unbondReadyAt);
    }

    function withdraw() external {
        Position storage p = positions[msg.sender];
        uint256 amt = p.unbonding;
        if (amt == 0) revert NothingUnbonding();
        if (block.timestamp < p.unbondReadyAt) revert StillUnbonding();
        p.unbonding = 0;
        token.transfer(msg.sender, amt);
        emit Withdrawn(msg.sender, amt);
    }

    // --------------------------- views ------------------------------------

    function isActiveWriter(address writer) external view returns (bool) {
        return allowlistedWriter[writer] && positions[writer].staked >= minWriterStake;
    }

    function isAllowlistedSigner(address signer) external view returns (bool) {
        return allowlistedSigner[signer];
    }

    // --------------------------- slashing ---------------------------------

    /// @notice Slash a writer's ACTIVE stake; never slashes beyond it. Half goes
    ///         to `beneficiary` (challenger bounty), the remainder is "burned".
    /// @dev Skeleton routes the burn remainder to `owner` (treasury). Production
    ///      sends it to a real burn sink. Only `unbonding` funds are shielded
    ///      (already exited active stake); production may also slash unbonding.
    function slash(address writer, uint256 amount, address beneficiary) external onlySlasher {
        Position storage p = positions[writer];
        uint256 amt = amount > p.staked ? p.staked : amount; // clamp: never below zero
        p.staked -= amt;
        totalStaked -= amt;
        uint256 bounty = amt / 2;
        uint256 burned = amt - bounty;
        if (bounty > 0) token.transfer(beneficiary, bounty);
        if (burned > 0) token.transfer(owner, burned); // TODO: real burn sink
        emit Slashed(writer, amt, beneficiary, burned);
    }

    // --------------------- owner / governance (Safe) -----------------------

    function setSlasher(address slasher_) external onlyOwner {
        slasher = slasher_;
        emit SlasherSet(slasher_);
    }

    function setWriter(address writer, bool allowed) external onlyOwner {
        allowlistedWriter[writer] = allowed;
        emit WriterAllowlisted(writer, allowed);
    }

    function setSigner(address signer, bool allowed) external onlyOwner {
        allowlistedSigner[signer] = allowed;
        emit SignerAllowlisted(signer, allowed);
    }

    function setMinWriterStake(uint256 v) external onlyOwner {
        minWriterStake = v;
    }

    function transferOwnership(address newOwner) external onlyOwner {
        if (newOwner == address(0)) revert ZeroAddress();
        owner = newOwner;
        emit OwnerSet(newOwner);
    }
}

// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.19;

/// @notice Staking/liability surface the attestation resolver and challenge
///         module depend on.
interface IStakingManager {
    /// @return true if `writer` is allowlisted AND meets the minimum active stake.
    function isActiveWriter(address writer) external view returns (bool);

    /// @return true if `signer` is an allowlisted detector signing key (k-of-n).
    function isAllowlistedSigner(address signer) external view returns (bool);

    /// @notice Slash a writer's active stake. Callable only by the slasher module
    ///         (the OptimisticChallenge contract) on a resolved dispute.
    function slash(address writer, uint256 amount, address beneficiary) external;
}

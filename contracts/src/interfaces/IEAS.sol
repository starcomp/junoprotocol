// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.19;

/// @notice Minimal VENDORED subset of the Ethereum Attestation Service types.
/// @dev Production MUST replace this with the audited
///      `@ethereum-attestation-service/eas-contracts` package. This subset
///      exists so the resolver compiles self-contained in this skeleton.

/// @dev EAS Attestation record passed to a SchemaResolver. Field order/types
///      match eas-contracts. `refUID` is where JIP-1's `parent_ref` lives
///      (near-dup parent linkage) and `data` holds the canonical attestation
///      bytes (see @juno-protocol/schema).
struct Attestation {
    bytes32 uid;
    bytes32 schema;
    uint64 time;
    uint64 expirationTime;
    uint64 revocationTime;
    bytes32 refUID;
    address recipient;
    address attester;
    bool revocable;
    bytes data;
}

/// @notice The resolver callback interface EAS invokes on attest/revoke.
interface ISchemaResolver {
    function isPayable() external pure returns (bool);
    function attest(Attestation calldata attestation) external payable returns (bool);
    function multiAttest(Attestation[] calldata attestations, uint256[] calldata values)
        external
        payable
        returns (bool);
    function revoke(Attestation calldata attestation) external payable returns (bool);
    function multiRevoke(Attestation[] calldata attestations, uint256[] calldata values)
        external
        payable
        returns (bool);
}

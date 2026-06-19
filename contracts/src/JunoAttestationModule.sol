// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.19;

import {Attestation} from "./interfaces/IEAS.sol";
import {SchemaResolver} from "./vendor/SchemaResolver.sol";
import {IStakingManager} from "./interfaces/IStakingManager.sol";

/// @title JunoAttestationModule
/// @notice EAS SchemaResolver enforcing Juno's MVP write-path invariants:
///         (1) `chash` EXACT dedup (the persistent-memory primary key), and
///         (2) the attester is a STAKED, allowlisted writer (economic liability).
///         k-of-n ECDSA verification over the signed content hash is present as a
///         STUB (`_verifyKOfN`) — see notes below and JIP (Trust-model).
/// @dev The canonical data layout is defined once in @juno-protocol/schema
///      (JIP-1). The abi.decode type list below MUST match it exactly; a CI guard
///      asserts no drift between the deployed EAS schema and the canonical layout.
contract JunoAttestationModule is SchemaResolver {
    IStakingManager public immutable staking;

    /// @notice k in k-of-n. Informational at MVP (single attester); the real
    ///         threshold check lives in `_verifyKOfN` once federation exists.
    uint8 public immutable kThreshold;

    uint8 public constant SCHEMA_VERSION = 1;
    uint8 public constant PROVENANCE_STAKED_REAL = 0;

    /// @notice chash => attestation uid. Nonzero means this exact content has
    ///         already been attested (exact dedup / persistent memory anchor).
    mapping(bytes32 => bytes32) public chashToUid;

    error AttesterNotActive(address attester);
    error DuplicateChash(bytes32 chash);
    error BadSchemaVersion(uint8 got);
    error MockMustUseUnstakedPath();
    error SignatureCheckFailed();

    event AttestationAccepted(
        bytes32 indexed uid, bytes32 indexed chash, address indexed attester, bytes lshBucket
    );
    event AttestationRevoked(bytes32 indexed uid, bytes32 indexed chash);

    constructor(address eas, IStakingManager staking_, uint8 kThreshold_) SchemaResolver(eas) {
        staking = staking_;
        kThreshold = kThreshold_;
    }

    function onAttest(Attestation calldata att, uint256 /*value*/ ) internal override returns (bool) {
        // (2) staked-writer gating — the economic-liability precondition.
        if (!staking.isActiveWriter(att.attester)) revert AttesterNotActive(att.attester);

        // Decode only the fields this path needs (tuple-skip keeps the stack small).
        // Type list MUST match @juno-protocol/schema EAS_SCHEMA_STRING (JIP-1).
        (
            uint8 schemaVersion,
            bytes32 chash,
            , // phashCommit
            bytes memory lshBucket,
            , , , , // verdict, confidence, modelLineage, detectorVersion
            , , // c2paManifestHash, segmentMapHash
            , // attesterSetId
            bytes memory sigRef,
            , // timestamp
            uint8 provenance
        ) = abi.decode(
            att.data,
            (uint8, bytes32, bytes32, bytes, uint8, uint16, uint16, uint16, bytes32, bytes32, uint32, bytes, uint64, uint8)
        );

        if (schemaVersion != SCHEMA_VERSION) revert BadSchemaVersion(schemaVersion);

        // Staked writers MUST NOT carry mock provenance; mock/stub attestations use
        // a separate, unstaked test key and are excluded from reward/slash paths.
        if (provenance != PROVENANCE_STAKED_REAL) revert MockMustUseUnstakedPath();

        // (1) chash exact dedup. First writer wins; duplicates revert.
        if (chashToUid[chash] != bytes32(0)) revert DuplicateChash(chash);

        // k-of-n signature gate (STUB — see _verifyKOfN).
        if (!_verifyKOfN(att, sigRef)) revert SignatureCheckFailed();

        chashToUid[chash] = att.uid;
        emit AttestationAccepted(att.uid, chash, att.attester, lshBucket);
        return true;
    }

    function onRevoke(Attestation calldata att, uint256 /*value*/ ) internal override returns (bool) {
        // Revocation is allowed. We deliberately do NOT clear chashToUid here:
        // whether a revoked chash may be re-attested is a governance policy
        // decision (TODO: JIP). Revocation propagation is handled by the indexer.
        emit AttestationRevoked(att.uid, _chashOf(att));
        return true;
    }

    // ----------------------------------------------------------------------
    // STUBS / TODO
    // ----------------------------------------------------------------------

    /// @dev STUB. Production MUST:
    ///   1. recompute h = keccak256(content) where `content` is the ABI encoding
    ///      of every canonical field EXCEPT sigRef (see @juno-protocol/schema
    ///      `contentEncode`), prefixed with an EIP-712 / domain separator;
    ///   2. split `sigRef` into 65-byte ECDSA signatures, `ecrecover` each;
    ///   3. require the recovered signers are DISTINCT and each
    ///      `staking.isAllowlistedSigner(signer)`;
    ///   4. require the distinct-valid count >= kThreshold.
    /// The skeleton performs only a shape check so the write path is exercisable.
    function _verifyKOfN(Attestation calldata, /* att */ bytes memory sigRef)
        internal
        view
        returns (bool)
    {
        return sigRef.length >= uint256(kThreshold) * 65;
    }

    /// @dev Prefix-decode the chash for events. Safe: schemaVersion(uint8) and
    ///      chash(bytes32) are the first two static head words, before any
    ///      dynamic field, so decoding the prefix reads them directly.
    function _chashOf(Attestation calldata att) private pure returns (bytes32 chash) {
        (, chash) = abi.decode(att.data, (uint8, bytes32));
    }
}

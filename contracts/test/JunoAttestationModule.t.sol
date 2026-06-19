// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.19;

import {Test} from "forge-std/Test.sol";
import {JunoAttestationModule} from "../src/JunoAttestationModule.sol";
import {StakingManager} from "../src/StakingManager.sol";
import {IStakingManager} from "../src/interfaces/IStakingManager.sol";
import {IERC20} from "../src/interfaces/IERC20.sol";
import {Attestation} from "../src/interfaces/IEAS.sol";
import {MockERC20} from "./mocks/MockERC20.sol";

/// @notice Unit tests for the two MVP write-path invariants (chash dedup +
///         staked-writer gating). The test contract impersonates the EAS
///         contract (the only allowed caller of the resolver).
/// @dev STUB-LEVEL: k-of-n signatures are shape-checked only (see
///      JunoAttestationModule._verifyKOfN); real-signature tests with vm.sign
///      land when _verifyKOfN is implemented.
contract JunoAttestationModuleTest is Test {
    JunoAttestationModule module;
    StakingManager staking;
    MockERC20 token;

    address writer = makeAddr("writer");
    uint8 constant K = 1;

    function setUp() public {
        token = new MockERC20();
        // minWriterStake = 0: allowlisting alone makes a writer "active" for these
        // resolver-focused tests. Stake accounting is covered by the invariant test.
        staking = new StakingManager(IERC20(address(token)), 0, 1 days);
        // this test contract is the "EAS" address allowed to call the resolver.
        module = new JunoAttestationModule(address(this), IStakingManager(address(staking)), K);
        staking.setWriter(writer, true);
    }

    function test_AcceptsValidAttestation() public {
        bytes32 chash = keccak256("c-ok");
        Attestation memory att = _att(writer, chash, 0, 1, K * 65);
        assertTrue(module.attest(att));
        assertEq(module.chashToUid(chash), att.uid);
    }

    function test_RevertWhen_AttesterNotStaked() public {
        address stranger = makeAddr("stranger");
        Attestation memory att = _att(stranger, keccak256("c1"), 0, 1, K * 65);
        vm.expectRevert(abi.encodeWithSelector(JunoAttestationModule.AttesterNotActive.selector, stranger));
        module.attest(att);
    }

    function test_RevertWhen_DuplicateChash() public {
        bytes32 chash = keccak256("dup");
        module.attest(_att(writer, chash, 0, 1, K * 65));
        Attestation memory att2 = _att(writer, chash, 0, 1, K * 65);
        vm.expectRevert(abi.encodeWithSelector(JunoAttestationModule.DuplicateChash.selector, chash));
        module.attest(att2);
    }

    function test_RevertWhen_MockProvenanceOnStakedPath() public {
        Attestation memory att = _att(writer, keccak256("c3"), 1 /* mock */, 1, K * 65);
        vm.expectRevert(JunoAttestationModule.MockMustUseUnstakedPath.selector);
        module.attest(att);
    }

    function test_RevertWhen_BadSchemaVersion() public {
        Attestation memory att = _att(writer, keccak256("c4"), 0, 2 /* bad */, K * 65);
        vm.expectRevert(abi.encodeWithSelector(JunoAttestationModule.BadSchemaVersion.selector, uint8(2)));
        module.attest(att);
    }

    function test_RevertWhen_TooFewSignatureBytes() public {
        Attestation memory att = _att(writer, keccak256("c5"), 0, 1, (K * 65) - 1);
        vm.expectRevert(JunoAttestationModule.SignatureCheckFailed.selector);
        module.attest(att);
    }

    function test_RevertWhen_CallerNotEAS() public {
        Attestation memory att = _att(writer, keccak256("c6"), 0, 1, K * 65);
        vm.prank(makeAddr("notEAS"));
        vm.expectRevert(); // SchemaResolver.AccessDenied()
        module.attest(att);
    }

    // ---------------------------- helpers ----------------------------------

    function _att(address attester, bytes32 chash, uint8 provenance, uint8 schemaVersion, uint256 sigLen)
        internal
        view
        returns (Attestation memory)
    {
        return Attestation({
            uid: keccak256(abi.encode(chash, attester, sigLen, provenance, schemaVersion)),
            schema: bytes32(uint256(1)),
            time: uint64(block.timestamp),
            expirationTime: 0,
            revocationTime: 0,
            refUID: bytes32(0),
            recipient: address(0),
            attester: attester,
            revocable: true,
            data: _data(chash, provenance, schemaVersion, sigLen)
        });
    }

    /// @dev Builds canonical attestation bytes matching @juno-protocol/schema /
    ///      JIP-1 (flat ABI list, same order the resolver decodes).
    function _data(bytes32 chash, uint8 provenance, uint8 schemaVersion, uint256 sigLen)
        internal
        pure
        returns (bytes memory)
    {
        bytes memory lshBucket = hex"a1b2c3";
        bytes memory sigRef = new bytes(sigLen);
        return abi.encode(
            schemaVersion, // uint8
            chash, // bytes32
            bytes32(0), // phashCommit
            lshBucket, // bytes
            uint8(1), // verdict
            uint16(9000), // confidence
            uint16(2), // modelLineage
            uint16(7), // detectorVersion
            bytes32(0), // c2paManifestHash
            bytes32(0), // segmentMapHash
            uint32(42), // attesterSetId
            sigRef, // bytes
            uint64(1718750000), // timestamp
            provenance // uint8
        );
    }
}

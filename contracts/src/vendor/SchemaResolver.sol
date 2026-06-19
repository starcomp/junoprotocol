// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.19;

import {Attestation, ISchemaResolver} from "../interfaces/IEAS.sol";

/// @title SchemaResolver (vendored minimal base)
/// @notice Abstract base mirroring eas-contracts' SchemaResolver: only the EAS
///         contract may call the callbacks, which delegate to `onAttest`/`onRevoke`.
/// @dev VENDORED skeleton — production MUST use the audited eas-contracts base.
abstract contract SchemaResolver is ISchemaResolver {
    error AccessDenied();
    error NotPayable();
    error InvalidEAS();

    address internal immutable _eas;

    constructor(address eas) {
        if (eas == address(0)) revert InvalidEAS();
        _eas = eas;
    }

    modifier onlyEAS() {
        if (msg.sender != _eas) revert AccessDenied();
        _;
    }

    /// @dev Override to true only if the resolver accepts ETH.
    function isPayable() public pure virtual returns (bool) {
        return false;
    }

    receive() external payable virtual {
        if (!isPayable()) revert NotPayable();
    }

    function attest(Attestation calldata attestation) external payable onlyEAS returns (bool) {
        return onAttest(attestation, msg.value);
    }

    function multiAttest(Attestation[] calldata attestations, uint256[] calldata values)
        external
        payable
        onlyEAS
        returns (bool)
    {
        uint256 length = attestations.length;
        for (uint256 i = 0; i < length; i++) {
            if (!onAttest(attestations[i], values[i])) return false;
        }
        return true;
    }

    function revoke(Attestation calldata attestation) external payable onlyEAS returns (bool) {
        return onRevoke(attestation, msg.value);
    }

    function multiRevoke(Attestation[] calldata attestations, uint256[] calldata values)
        external
        payable
        onlyEAS
        returns (bool)
    {
        uint256 length = attestations.length;
        for (uint256 i = 0; i < length; i++) {
            if (!onRevoke(attestations[i], values[i])) return false;
        }
        return true;
    }

    function onAttest(Attestation calldata attestation, uint256 value) internal virtual returns (bool);

    function onRevoke(Attestation calldata attestation, uint256 value) internal virtual returns (bool);
}

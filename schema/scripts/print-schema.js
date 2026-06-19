'use strict';
/**
 * Prints the canonical schema in every representation that downstream code must
 * match: the EAS schema string, the Solidity decode tuple, and the Rust/Borsh
 * struct. Run: `npm run print-schema` (from schema/).
 *
 * Use this output verbatim when:
 *   - registering the schema with EAS SchemaRegistry (the EAS string),
 *   - writing abi.decode(...) in the Solidity resolver (the tuple),
 *   - defining the Anchor account/leaf struct on Solana (the Rust struct).
 */
const C = require('./../src/canonical');
const { solidityDecodeTuple } = require('./../src/eas');
const { rustStruct } = require('./../src/borsh');

console.log('=== EAS schema string (SchemaRegistry.register) ===');
console.log(C.EAS_SCHEMA_STRING);
console.log('\n=== Solidity decode tuple (abi.decode) ===');
console.log('abi.decode(data, ' + solidityDecodeTuple() + ')');
console.log('\n=== Canonical struct (Solidity memory struct) ===');
console.log('struct CanonicalAttestation {');
for (const f of C.FIELDS) console.log(`    ${f.sol} ${f.name};`);
console.log('}');
console.log('\n=== Rust / Borsh struct (mainnet-conditional, Solana) ===');
console.log(rustStruct());
console.log('\n=== Notes ===');
console.log('- parent_ref (JIP-1) is NOT here: it maps to EAS native refUID / a Solana leaf pointer.');
console.log('- sigRef is excluded from the signed content hash (detectors sign keccak256 of all other fields).');

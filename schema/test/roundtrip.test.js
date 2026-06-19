'use strict';
/**
 * JIP-1 round-trip equivalence test (dependency-free; runs on Node >= 12).
 *
 * Proves:
 *  1. EAS (ABI) encode -> decode is lossless.
 *  2. Borsh encode -> decode is lossless.
 *  3. Field ORDER and SET are identical across EAS and Borsh (by construction,
 *     asserted explicitly) — the canonical layout cannot drift between chains.
 *  4. Cross-representation equivalence: the object recovered from EAS equals the
 *     object recovered from Borsh equals the original.
 *  5. Edge cases: empty dynamic bytes and max-width uints.
 *  6. (optional) Faithfulness: our hand-written ABI coder matches ethers'
 *     defaultAbiCoder byte-for-byte, IF ethers is installed.
 *
 * Exit code: non-zero on any failure (assert throws).
 */
const assert = require('assert');
const C = require('../src/canonical');
const { encodeEAS, decodeEAS, contentEncode, solidityDecodeTuple } = require('../src/eas');
const { borshEncode, borshDecode } = require('../src/borsh');
const { FIELDS, SAMPLE, diff, EAS_SCHEMA_STRING } = C;

let passed = 0;
function check(name, fn) {
  fn();
  passed++;
  console.log('  ✓ ' + name);
}
function assertEq(a, b, label) {
  const d = diff(a, b);
  assert.ok(d.ok, `${label}: field "${d.field}" differs (${d.a} !== ${d.b})`);
}

console.log('JIP-1 canonical attestation — round-trip equivalence');
console.log('  schema: ' + EAS_SCHEMA_STRING);
console.log('  solidity decode tuple: ' + solidityDecodeTuple());

check('EAS encode→decode is lossless', () => {
  assertEq(decodeEAS(encodeEAS(SAMPLE)), SAMPLE, 'EAS round-trip');
});

check('Borsh encode→decode is lossless', () => {
  assertEq(borshDecode(borshEncode(SAMPLE)), SAMPLE, 'Borsh round-trip');
});

check('EAS and Borsh enumerate identical fields in identical order', () => {
  // Both codecs iterate FIELDS; assert FIELDS itself is the single ordering and
  // that every field carries both an EAS and a Borsh type (no half-defined field).
  const names = FIELDS.map((f) => f.name);
  assert.deepStrictEqual(names, Array.from(new Set(names)), 'duplicate field name');
  for (const f of FIELDS) {
    assert.ok(f.eas && f.kind, `field ${f.name} missing EAS type/kind`);
    assert.ok(f.borsh, `field ${f.name} missing Borsh type`);
    assert.ok(f.sol, `field ${f.name} missing Solidity type`);
  }
});

check('cross-representation: EAS-decoded === Borsh-decoded === original', () => {
  const fromEas = decodeEAS(encodeEAS(SAMPLE));
  const fromBorsh = borshDecode(borshEncode(SAMPLE));
  assertEq(fromEas, fromBorsh, 'EAS-vs-Borsh');
  assertEq(fromEas, SAMPLE, 'EAS-vs-original');
});

check('edge: empty dynamic bytes (lshBucket, sigRef = 0x)', () => {
  const o = Object.assign({}, SAMPLE, { lshBucket: '0x', sigRef: '0x' });
  assertEq(decodeEAS(encodeEAS(o)), o, 'EAS empty-bytes');
  assertEq(borshDecode(borshEncode(o)), o, 'Borsh empty-bytes');
});

check('edge: max-width uints (u8/u16/u32/u64 maxima)', () => {
  const o = Object.assign({}, SAMPLE, {
    schemaVersion: 255, verdict: 255, provenance: 255,
    confidence: 65535, modelLineage: 65535, detectorVersion: 65535,
    attesterSetId: 4294967295, timestamp: 18446744073709551615n,
  });
  assertEq(decodeEAS(encodeEAS(o)), o, 'EAS max-uints');
  assertEq(borshDecode(borshEncode(o)), o, 'Borsh max-uints');
});

check('contentEncode excludes sigRef (signed payload)', () => {
  const a = contentEncode(SAMPLE);
  const b = contentEncode(Object.assign({}, SAMPLE, { sigRef: '0x' + 'cd'.repeat(65) }));
  assert.strictEqual(a, b, 'content hash payload must not depend on sigRef');
  const c = contentEncode(Object.assign({}, SAMPLE, { verdict: 0 }));
  assert.notStrictEqual(a, c, 'content payload must depend on a real field (verdict)');
});

// (6) optional faithfulness cross-check against ethers
let ethers = null;
try { ethers = require('ethers'); } catch (_) { /* not installed */ }
if (ethers && ethers.utils && ethers.utils.defaultAbiCoder) {
  check('faithfulness: hand-written ABI === ethers defaultAbiCoder', () => {
    const coder = ethers.utils.defaultAbiCoder;
    const types = FIELDS.map((f) => f.eas);
    const values = FIELDS.map((f) => (f.kind === 'uint'
      ? ethers.BigNumber.from(BigInt(SAMPLE[f.name]).toString())
      : SAMPLE[f.name]));
    const ref = coder.encode(types, values).toLowerCase();
    assert.strictEqual(encodeEAS(SAMPLE).toLowerCase(), ref, 'ABI encoding mismatch vs ethers');
  });
} else {
  console.log('  ⚠ ethers not installed — skipped ABI faithfulness cross-check (CI runs it on Node 20)');
}

console.log(`\nOK — ${passed} checks passed.`);

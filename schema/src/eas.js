'use strict';
/**
 * EAS codec — the on-chain (testnet/L2) representation.
 *
 * EAS stores an attestation's `data` as the Solidity ABI encoding of the schema
 * tuple, and the resolver decodes it with `abi.decode(data, (<types...>))`.
 * This module implements that exact canonical ABI head/tail scheme with ZERO
 * dependencies so it runs anywhere. test/roundtrip.test.js additionally
 * cross-checks the output against ethers' defaultAbiCoder when ethers is
 * installed, proving byte-for-byte fidelity with a battle-tested ABI coder.
 */
const C = require('./canonical');
const { FIELDS, SIG_FIELD, hexToBuf, bufToHex, uintToWord, wordToUint, pad32 } = C;

function isDynamic(f) { return f.kind === 'bytes'; }

// abi.encode(<field values in canonical order>) -> 0x-hex
function encodeEAS(obj) {
  const head = Buffer.alloc(32 * FIELDS.length);
  const tails = [];
  let tailOffset = 32 * FIELDS.length;

  FIELDS.forEach((f, i) => {
    const slot = i * 32;
    if (isDynamic(f)) {
      uintToWord(BigInt(tailOffset)).copy(head, slot); // head holds the offset
      const data = hexToBuf(obj[f.name]);
      const tail = Buffer.concat([uintToWord(BigInt(data.length)), pad32(data)]);
      tails.push(tail);
      tailOffset += tail.length;
    } else if (f.kind === 'uint') {
      uintToWord(BigInt(obj[f.name])).copy(head, slot); // right-aligned
    } else { // bytes32 — left-aligned, exactly one word
      const b = hexToBuf(obj[f.name]);
      if (b.length !== 32) throw new Error(`${f.name}: bytes32 must be 32 bytes, got ${b.length}`);
      b.copy(head, slot);
    }
  });

  return bufToHex(Buffer.concat([head, ...tails]));
}

// abi.decode -> canonical object (uints as BigInt, bytes/bytes32 as 0x-hex)
function decodeEAS(hex) {
  const buf = hexToBuf(hex);
  const out = {};
  FIELDS.forEach((f, i) => {
    const word = buf.slice(i * 32, i * 32 + 32);
    if (isDynamic(f)) {
      const off = Number(wordToUint(word));
      const len = Number(wordToUint(buf.slice(off, off + 32)));
      out[f.name] = bufToHex(buf.slice(off + 32, off + 32 + len));
    } else if (f.kind === 'uint') {
      out[f.name] = wordToUint(word);
    } else {
      out[f.name] = bufToHex(word);
    }
  });
  return out;
}

// The signed-content encoding: every canonical field EXCEPT sigRef, ABI-encoded.
// Detectors sign keccak256(contentEncode(obj)); the resolver recomputes & verifies.
function contentEncode(obj) {
  const fields = FIELDS.filter((f) => f.name !== SIG_FIELD);
  const head = Buffer.alloc(32 * fields.length);
  const tails = [];
  let tailOffset = 32 * fields.length;
  fields.forEach((f, i) => {
    const slot = i * 32;
    if (isDynamic(f)) {
      uintToWord(BigInt(tailOffset)).copy(head, slot);
      const data = hexToBuf(obj[f.name]);
      const tail = Buffer.concat([uintToWord(BigInt(data.length)), pad32(data)]);
      tails.push(tail);
      tailOffset += tail.length;
    } else if (f.kind === 'uint') {
      uintToWord(BigInt(obj[f.name])).copy(head, slot);
    } else {
      hexToBuf(obj[f.name]).copy(head, slot);
    }
  });
  return bufToHex(Buffer.concat([head, ...tails]));
}

// The Solidity decode tuple type list, e.g. "(uint8,bytes32,...)".
function solidityDecodeTuple() { return '(' + FIELDS.map((f) => f.sol).join(',') + ')'; }

module.exports = { encodeEAS, decodeEAS, contentEncode, solidityDecodeTuple };

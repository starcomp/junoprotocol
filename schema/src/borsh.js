'use strict';
/**
 * Borsh codec — the mainnet-conditional (Solana/Anchor) representation.
 *
 * Borsh is little-endian and length-prefixes variable-length sequences. This is
 * a minimal, dependency-free implementation of exactly the subset our canonical
 * struct needs (u8/u16/u32/u64, fixed [u8;32], and Vec<u8>), matching the Rust
 * `#[derive(BorshSerialize, BorshDeserialize)] struct JunoAttestation` printed
 * by scripts/print-schema.js. Field order is identical to the EAS encoding
 * because both iterate the same FIELDS array.
 */
const C = require('./canonical');
const { FIELDS, hexToBuf, bufToHex } = C;

function uintToLE(big, nbytes) {
  const buf = Buffer.alloc(nbytes);
  let v = BigInt(big);
  for (let i = 0; i < nbytes; i++) { buf[i] = Number(v & 0xffn); v >>= 8n; }
  if (v !== 0n) throw new Error(`uint overflow for ${nbytes}-byte field`);
  return buf;
}
const INT_BYTES = { u8: 1, u16: 2, u32: 4, u64: 8 };

function borshEncode(obj) {
  const parts = [];
  for (const f of FIELDS) {
    if (INT_BYTES[f.borsh]) {
      parts.push(uintToLE(obj[f.name], INT_BYTES[f.borsh]));
    } else if (f.borsh === '[u8;32]') {
      const b = hexToBuf(obj[f.name]);
      if (b.length !== 32) throw new Error(`${f.name}: [u8;32] must be 32 bytes, got ${b.length}`);
      parts.push(b);
    } else if (f.borsh === 'Vec<u8>') {
      const b = hexToBuf(obj[f.name]);
      parts.push(uintToLE(b.length, 4)); // u32 LE length prefix
      parts.push(b);
    } else {
      throw new Error(`unhandled borsh type ${f.borsh}`);
    }
  }
  return Buffer.concat(parts);
}

function borshDecode(buf) {
  let o = 0;
  const out = {};
  const readLE = (n) => {
    let v = 0n;
    for (let i = 0; i < n; i++) v |= BigInt(buf[o + i]) << (8n * BigInt(i));
    o += n;
    return v;
  };
  for (const f of FIELDS) {
    if (INT_BYTES[f.borsh]) {
      out[f.name] = readLE(INT_BYTES[f.borsh]);
    } else if (f.borsh === '[u8;32]') {
      out[f.name] = bufToHex(buf.slice(o, o + 32)); o += 32;
    } else if (f.borsh === 'Vec<u8>') {
      const len = Number(readLE(4));
      out[f.name] = bufToHex(buf.slice(o, o + len)); o += len;
    }
  }
  if (o !== buf.length) throw new Error(`borsh: ${buf.length - o} trailing byte(s) after decode`);
  return out;
}

// The Rust struct mainnet would use, derived from the same FIELDS.
function rustStruct() {
  const lines = FIELDS.map((f) => {
    const snake = f.name.replace(/[A-Z]/g, (m) => '_' + m.toLowerCase());
    return `    pub ${snake}: ${f.borsh.replace('Vec<u8>', 'Vec<u8>').replace('[u8;32]', '[u8; 32]')},`;
  });
  return '#[derive(BorshSerialize, BorshDeserialize)]\npub struct JunoAttestation {\n' + lines.join('\n') + '\n}';
}

module.exports = { borshEncode, borshDecode, rustStruct };

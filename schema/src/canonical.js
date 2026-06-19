'use strict';
/**
 * Juno Protocol — canonical attestation object (JIP-1), single source of truth.
 *
 * The FIELDS array below is THE definition. Everything else — the EAS schema
 * string, the Solidity decode tuple, the Rust/Borsh struct, the TS types, and
 * both codecs (src/eas.js, src/borsh.js) — is derived from it, in this exact
 * order, so the two on-chain representations can never silently drift.
 *
 * IMPORTANT — two JIP-1 fields are NOT in this data layout, by design:
 *   - parent_ref : realized as EAS's NATIVE `refUID` field on the Attestation
 *                  struct (and as a leaf pointer on Solana). It is attestation
 *                  metadata, not schema data, so it is not ABI/Borsh-encoded here.
 *   - (EAS also has a native `time` field; our `timestamp` below is the DETECTION
 *      time, which may differ from the on-chain attestation time, so we keep it.)
 *
 * Signing note (sigRef): detectors sign over the keccak256 of all canonical
 * fields EXCEPT `sigRef` (you cannot sign bytes that contain the signature).
 * The on-chain resolver recomputes that content hash and verifies k-of-n.
 * See src/eas.js `contentEncode()` and contracts/src/JunoAttestationModule.sol.
 */

// kind: 'uint' | 'bytes32' | 'bytes'   (drives the ABI coder)
// borsh: the Rust/Borsh type            (drives the Borsh coder)
const FIELDS = [
  { name: 'schemaVersion',    eas: 'uint8',   kind: 'uint',    borsh: 'u8',      sol: 'uint8'   },
  { name: 'chash',            eas: 'bytes32', kind: 'bytes32', borsh: '[u8;32]', sol: 'bytes32' },
  { name: 'phashCommit',      eas: 'bytes32', kind: 'bytes32', borsh: '[u8;32]', sol: 'bytes32' },
  { name: 'lshBucket',        eas: 'bytes',   kind: 'bytes',   borsh: 'Vec<u8>', sol: 'bytes'   },
  { name: 'verdict',          eas: 'uint8',   kind: 'uint',    borsh: 'u8',      sol: 'uint8'   },
  { name: 'confidence',       eas: 'uint16',  kind: 'uint',    borsh: 'u16',     sol: 'uint16'  },
  { name: 'modelLineage',     eas: 'uint16',  kind: 'uint',    borsh: 'u16',     sol: 'uint16'  },
  { name: 'detectorVersion',  eas: 'uint16',  kind: 'uint',    borsh: 'u16',     sol: 'uint16'  },
  { name: 'c2paManifestHash', eas: 'bytes32', kind: 'bytes32', borsh: '[u8;32]', sol: 'bytes32' },
  { name: 'segmentMapHash',   eas: 'bytes32', kind: 'bytes32', borsh: '[u8;32]', sol: 'bytes32' },
  { name: 'attesterSetId',    eas: 'uint32',  kind: 'uint',    borsh: 'u32',     sol: 'uint32'  },
  { name: 'sigRef',           eas: 'bytes',   kind: 'bytes',   borsh: 'Vec<u8>', sol: 'bytes'   },
  { name: 'timestamp',        eas: 'uint64',  kind: 'uint',    borsh: 'u64',     sol: 'uint64'  },
  { name: 'provenance',       eas: 'uint8',   kind: 'uint',    borsh: 'u8',      sol: 'uint8'   },
];

// Field that is NEVER part of the signed content hash.
const SIG_FIELD = 'sigRef';

const SCHEMA_VERSION = 1;

// The registerable EAS schema string (what you pass to EAS SchemaRegistry.register()).
const EAS_SCHEMA_STRING = FIELDS.map((f) => `${f.eas} ${f.name}`).join(',');

// Verdict / provenance / lineage enums (mirror JIP-1).
const VERDICT = { NOT: 0, WATERMARKED: 1, UNCERTAIN: 2 };
const PROVENANCE = { STAKED_REAL: 0, MOCK: 1 };

// ---- low-level helpers (shared by both codecs; dependency-free) ----------

function stripHex(h) { return String(h).replace(/^0x/i, ''); }
function hexToBuf(h) {
  const s = stripHex(h);
  if (s.length % 2 !== 0) throw new Error(`odd-length hex: ${h}`);
  return Buffer.from(s, 'hex');
}
function bufToHex(b) { return '0x' + Buffer.from(b).toString('hex'); }
function uintToWord(big) {
  // 32-byte big-endian (right-aligned), as ABI encodes uintN.
  const hex = BigInt(big).toString(16);
  if (hex.length > 64) throw new Error('uint overflow > 256 bits');
  return Buffer.from(hex.padStart(64, '0'), 'hex');
}
function wordToUint(buf) { return BigInt('0x' + Buffer.from(buf).toString('hex')); }
function pad32(buf) {
  const r = buf.length % 32;
  return r === 0 ? Buffer.from(buf) : Buffer.concat([buf, Buffer.alloc(32 - r)]);
}

// A representative, fully-populated sample attestation for tests/demos.
// (Values are illustrative; bytes are hex strings, uints are Number/BigInt.)
const SAMPLE = Object.freeze({
  schemaVersion: SCHEMA_VERSION,
  chash: '0x' + '11'.repeat(32),
  phashCommit: '0x' + '22'.repeat(32),
  lshBucket: '0xa1b2c3d4e5f6', // variable-length locality-preserving bucket key
  verdict: VERDICT.WATERMARKED,
  confidence: 9000, // basis points
  modelLineage: 2, // e.g. Imagen
  detectorVersion: 7,
  c2paManifestHash: '0x' + '33'.repeat(32),
  segmentMapHash: '0x' + '44'.repeat(32),
  attesterSetId: 42,
  sigRef: '0x' + 'ab'.repeat(65), // one 65-byte ECDSA signature (r||s||v)
  timestamp: 1718750000n, // BigInt (u64) — detection time
  provenance: PROVENANCE.STAKED_REAL,
});

// Canonicalize an attestation to a comparable, representation-independent shape:
// uints -> decimal string (via BigInt), bytes/bytes32 -> lowercase 0x-hex.
function canon(obj) {
  const out = {};
  for (const f of FIELDS) {
    const v = obj[f.name];
    if (f.kind === 'uint') out[f.name] = BigInt(v).toString();
    else out[f.name] = ('0x' + stripHex(v).toLowerCase());
  }
  return out;
}
// Returns {ok:true} or {ok:false, field, a, b}.
function diff(a, b) {
  const ca = canon(a), cb = canon(b);
  for (const f of FIELDS) {
    if (ca[f.name] !== cb[f.name]) return { ok: false, field: f.name, a: ca[f.name], b: cb[f.name] };
  }
  return { ok: true };
}

module.exports = {
  FIELDS, SIG_FIELD, SCHEMA_VERSION, EAS_SCHEMA_STRING, VERDICT, PROVENANCE, SAMPLE,
  stripHex, hexToBuf, bufToHex, uintToWord, wordToUint, pad32, canon, diff,
};

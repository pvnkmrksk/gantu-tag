#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Pavan Kumar Kaushik. Part of gantu-tag, https://github.com/pvnkmrksk/gantu-tag (see NOTICE).
"""Decode a gantu tag's Hubble advert (service data of UUID 0xFCA6, AES-EAX, protocol v2) with its key.

Usage:  python3 tools/hubble_decode.py ~/gantu-keys/hagalu_002.hubble.key 08bd470d7219e1d96ffe3c...
        (one or more service-data hex strings, e.g. copied from nRF Connect)

Checks that the rotating ID (EID) matches the key, verifies the AEAD tag and decrypts the payload; a 7-byte
payload is printed as VCC, temperature and advertising count (see docs/programming.md). parse_sensors() is the
same parser a dashboard needs for the payloads Hubble's API and webhooks return (base64, already decrypted).
Independent re-implementation of pyhubblenetwork's decrypt_eax() (Apache-2.0). Needs: pip3 install cryptography
"""
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.cmac import CMAC

VCC_UNIT, TEMP_UNIT = 0.03125, 0.01   # V and degC per count (vccUnit, tempUnit in the .cfg)


def parse_sensors(payload: bytes) -> dict:
    """7-byte gantu sensor payload: VCC (1), temperature (2, signed), advertising count (4); little-endian."""
    if len(payload) != 7:
        raise ValueError(f"expected 7 bytes, got {len(payload)}")
    return {"vcc_v": round(payload[0] * VCC_UNIT, 3),
            "temp_c": round(int.from_bytes(payload[1:3], "little", signed=True) * TEMP_UNIT, 2),
            "adv_count": int.from_bytes(payload[3:7], "little")}


def _ecb(key, block):
    e = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
    return e.update(block) + e.finalize()


def _omac(key, t, data):
    c = CMAC(algorithms.AES(key))
    c.update(bytes(15) + bytes([t]) + data)
    return c.finalize()


def _eax_decrypt(key, nonce, ct, tag):
    n, h, c = _omac(key, 0, nonce), _omac(key, 1, b""), _omac(key, 2, ct)
    if bytes(a ^ b ^ d for a, b, d in zip(n, h, c))[:len(tag)] != tag:
        return None
    d = Cipher(algorithms.AES(key), modes.CTR(n)).decryptor()
    return d.update(ct) + d.finalize()


def _eid(key, counter, rot):
    key0 = _ecb(key, bytes(11) + b"\xff\x00\x00" + counter.to_bytes(4, "little")[2:4][::-1])
    return int.from_bytes(_ecb(key0, bytes(11) + bytes([rot]) + counter.to_bytes(4, "big"))[:8], "big")


def decode(key: bytes, rot: int, raw: bytes) -> str:
    if raw[0] >> 2 != 2:
        return f"protocol version {raw[0] >> 2}, not AES-EAX (2)"
    salt, eid = raw[1:3], int.from_bytes(raw[3:11], "little")
    ct, tag = raw[11:-4], raw[-4:]
    idx = next((i for i in range(128) if _eid(key, i << rot, rot) == eid), None)
    if idx is None:
        return f"rotating ID doesn't match this key and period exponent {rot}"
    pt = _eax_decrypt(key, (idx << rot).to_bytes(4, "big") + salt, ct, tag)
    if pt is None:
        return f"ID matches (period {idx}) but the auth tag fails: damaged packet or wrong layout"
    out = f"OK, period {idx} since power-up, salt {salt.hex()}, payload {pt.hex()}"
    if len(pt) == 7:
        s = parse_sensors(pt)
        out += f" -> VCC {s['vcc_v']:.3f} V, {s['temp_c']:.2f} degC, advert {s['adv_count']}"
    return out


def main():
    if len(sys.argv) < 3:
        sys.exit("usage: python3 tools/hubble_decode.py <name>.hubble.key <service data hex> [...]")
    kv = dict(l.split(": ", 1) for l in open(sys.argv[1]).read().splitlines()
              if ": " in l and not l.startswith("#"))
    key, rot = bytes.fromhex(kv["key_hex"].strip()), int(kv["period_exponent"])
    for h in sys.argv[2:]:
        print(f"{h}: {decode(key, rot, bytes.fromhex(h))}")


if __name__ == "__main__":
    main()

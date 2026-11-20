#!/usr/bin/env python3
"""Make a Find My (OpenHaystack static-key) identity and .cfg for one gantu tag.

Usage:  python3 tools/new_findmy_tag.py hagalu_03                    new key pair + config
        python3 tools/new_findmy_tag.py hagalu_03 --adv-key BASE64   config for a key you already have
                                        [--interval 3] [--tx 0] [--template FILE]

Writes (never overwrites), mode 600, to $GANTU_KEYS (default ~/gantu-keys):
  <name>.keys          private + advertisement key (KEEP PRIVATE, never commit); not written with --adv-key
  <name>.findmy.cfg    load this in InPlay's NanoBeacon Config Tool
If $GANTU_FETCH_DIR is set, the private key is also written there as <name>.b64, for a report fetcher.

The template is configs/findmy-template.cfg (3 s, 0 dBm, non-connectable, static random address, XO cap code 8)
with the key bytes zeroed. The advert is OpenHaystack's: address key[0] | 0xC0, key[1..5]; payload
1E FF 4C 00 12 19 00 <key 6-27> <key[0] >> 6> 00. The .cfg stores the address as scanners show it.
Needs: pip3 install cryptography (only to make a new key pair).
"""
import argparse, base64, binascii, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = next((p for p in (os.path.join(HERE, "..", "configs", "findmy-template.cfg"),  # in the repo
                  os.path.join(HERE, "findmy-template.cfg")) if os.path.exists(p)),      # downloaded alongside
                 "findmy-template.cfg")
KEYS_DIR = os.path.expanduser(os.environ.get("GANTU_KEYS", "~/gantu-keys"))
FETCH_DIR = os.environ.get("GANTU_FETCH_DIR")


def new_key_pair():
    from cryptography.hazmat.primitives.asymmetric import ec
    k = ec.generate_private_key(ec.SECP224R1())
    priv = k.private_numbers().private_value.to_bytes(28, "big")
    adv = k.public_key().public_numbers().x.to_bytes(28, "big")
    return priv, adv


def findmy_fields(adv: bytes):
    """Address (as scanners show it) and the 29 data bytes after the 1E FF header."""
    addr = bytes([adv[0] | 0xC0]) + adv[1:6]                       # static random address
    data = bytes([0x4C, 0x00, 0x12, 0x19, 0x00]) + adv[6:28] + bytes([adv[0] >> 6, 0x00])
    assert len(data) == 29
    return addr, data


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("name", help="tag name, e.g. hagalu_03")
    ap.add_argument("--adv-key", help="existing advertisement (public) key, base64 (28 bytes)")
    ap.add_argument("--interval", type=int, default=3, help="seconds (default 3)")
    ap.add_argument("--tx", type=int, default=0, choices=range(-4, 5), help="dBm (default 0)")
    ap.add_argument("--template", default=TEMPLATE, help="default: configs/findmy-template.cfg")
    ap.add_argument("--out-dir", default=KEYS_DIR, help="default: $GANTU_KEYS or ~/gantu-keys")
    a = ap.parse_args()

    keys_path = os.path.join(a.out_dir, f"{a.name}.keys")
    cfg_path = os.path.join(a.out_dir, f"{a.name}.findmy.cfg")
    for p in ([cfg_path] if a.adv_key else [keys_path, cfg_path]):
        if os.path.exists(p):
            sys.exit(f"{p} already exists - pick another name (one key per tag).")

    priv = None
    if a.adv_key:
        try:
            adv = base64.b64decode(a.adv_key, validate=True)
        except binascii.Error:
            sys.exit("--adv-key is not base64")
        if len(adv) != 28:
            sys.exit(f"advertisement key must be 28 bytes, got {len(adv)}")
    else:
        priv, adv = new_key_pair()
    addr, data = findmy_fields(adv)

    cfg = json.load(open(a.template))
    s = cfg["advSet"][0]
    if s["payload"][0]["type"] != 255 or not s["payload"][0]["data"].lower().startswith("4c001219"):
        sys.exit(f"{a.template} doesn't look like a Find My config")
    s.update(bdAddr=addr.hex(), addrType="static", interval=a.interval * 1000)
    s["payload"][0].update(len=30, data=data[:2].hex() + data[2:].hex().upper())  # as the tool saves it
    cfg["txSetting"]["txPower"] = a.tx

    b64 = lambda b: base64.b64encode(b).decode()
    os.makedirs(a.out_dir, exist_ok=True)
    old = os.umask(0o077)
    if priv:
        with open(keys_path, "w") as f:
            f.write(f"# gantu tag {a.name} - OpenHaystack (Find My) key. KEEP PRIVATE: never commit or share.\n"
                    f"Private key: {b64(priv)}\n"
                    f"Advertisement key: {b64(adv)}\n"
                    f"Hashed adv key: {b64(hashlib.sha256(adv).digest())}\n")
    with open(cfg_path, "w") as f:
        json.dump(cfg, f, indent=4)
    fetch_note = ""
    if priv and FETCH_DIR:
        p = os.path.join(os.path.expanduser(FETCH_DIR), f"{a.name}.b64")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(b64(priv))
        fetch_note = f"\nFetcher key: {p}"
    os.umask(old)

    colon = lambda b: ":".join(f"{x:02X}" for x in b)
    print(f"""
Tag: {a.name}   Find My, {a.interval} s, {a.tx} dBm
Config:   {cfg_path}{"" if not priv else chr(10) + "Key file: " + keys_path}{fetch_note}

NanoBeacon Config Tool: Load the config, power-cycle the tag, Probe and Connect at once, Run in RAM.
(By hand instead: advertising set #1 -> Custom -> only Manufacturer Specific Data, ID 0x004C,
 Data {data[2:].hex().upper()}, address typed byte-reversed: {colon(addr[::-1])}.)

A scanner that shows addresses should then see
  Address:  {colon(addr)}
  Raw data: 0x1EFF{data.hex().upper()}   (31 bytes, no flags field)
""")


if __name__ == "__main__":
    main()

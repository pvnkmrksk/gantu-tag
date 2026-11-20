/* gantu-tag: turn a key into a NanoBeacon Config Tool .cfg, in the browser. MIT licence.
 *
 * Same output as tools/new_findmy_tag.py and tools/new_hubble_tag.py: the templates in configs/ with the key
 * written in, byte for byte. Nothing is sent anywhere: the key stays in this page.
 * Find My key pairs are NIST P-224 (as OpenHaystack), generated with crypto.getRandomValues.
 */
const GantuCfg = (() => {
  // ---- bytes ----
  const hex = (b) => Array.from(b, (x) => x.toString(16).padStart(2, "0")).join("");
  const fromHex = (s) => Uint8Array.from(s.match(/../g).map((h) => parseInt(h, 16)));
  const b64 = (b) => btoa(String.fromCharCode(...b));
  const fromB64 = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));
  const colon = (b) => Array.from(b, (x) => x.toString(16).padStart(2, "0").toUpperCase()).join(":");
  const toBig = (b) => BigInt("0x" + (hex(b) || "0"));
  const toBytes = (x, n) => fromHex(x.toString(16).padStart(2 * n, "0"));

  // ---- NIST P-224 ----
  const P = 2n ** 224n - 2n ** 96n + 1n;
  const A = P - 3n;
  const N = 0xffffffffffffffffffffffffffff16a2e0b8f03e13dd29455c5c2a3dn;
  const G = [0xb70e0cbd6bb4bf7f321390b94a03c1d356c21122343280d6115c1d21n,
             0xbd376388b5f723fb4c22dfe6cd4375a05a07476444d5819985007e34n];
  const mod = (a) => ((a % P) + P) % P;
  function inv(a) {                       // extended Euclid, a != 0 mod P
    let [r0, r1, s0, s1] = [mod(a), P, 1n, 0n];
    while (r1) { const q = r0 / r1; [r0, r1] = [r1, r0 - q * r1]; [s0, s1] = [s1, s0 - q * s1]; }
    return mod(s0);
  }
  function add(p, q) {
    if (!p) return q;
    if (!q) return p;
    if (p[0] === q[0] && mod(p[1] + q[1]) === 0n) return null;
    const l = p[0] === q[0] && p[1] === q[1]
      ? mod((3n * p[0] * p[0] + A) * inv(2n * p[1]))
      : mod((q[1] - p[1]) * inv(q[0] - p[0]));
    const x = mod(l * l - p[0] - q[0]);
    return [x, mod(l * (p[0] - x) - p[1])];
  }
  function mul(k, pt) {
    let r = null;
    for (const bit of k.toString(2)) { r = add(r, r); if (bit === "1") r = add(r, pt); }
    return r;
  }
  /** Advertisement (public) key: the 28-byte x coordinate of d·G. */
  const publicKey = (priv) => toBytes(mul(toBig(priv), G)[0], 28);
  function newKeyPair() {
    for (;;) {
      const priv = crypto.getRandomValues(new Uint8Array(28));
      const d = toBig(priv);
      if (d > 0n && d < N) return { priv, adv: publicKey(priv) };
    }
  }
  async function keysFile(name, priv, adv) {
    const h = new Uint8Array(await crypto.subtle.digest("SHA-256", adv));
    return `# gantu tag ${name} - OpenHaystack (Find My) key. KEEP PRIVATE: never commit or share.\n` +
      `Private key: ${b64(priv)}\nAdvertisement key: ${b64(adv)}\nHashed adv key: ${b64(h)}\n`;
  }

  // ---- configs ----
  const FM_ADDR = '"bdAddr": "c00000000000"';
  const FM_DATA = '"data": "4c00121900' + "0".repeat(48) + '"';
  const HB_KEY = '"key0": "' + "0".repeat(32) + '"';
  function replaceOnce(text, from, to) {
    const i = text.indexOf(from);
    if (i < 0 || text.indexOf(from, i + 1) >= 0) throw new Error("template doesn't look right: " + from);
    return text.slice(0, i) + to + text.slice(i + from.length);
  }
  function parseAdvKey(s) {
    let b;
    try { b = fromB64(s.trim()); } catch (e) { throw new Error("The advertisement key isn't base64."); }
    if (b.length !== 28) throw new Error(`The advertisement key must be 28 bytes; this is ${b.length}.`);
    return b;
  }
  /** Find My .cfg text, plus what a scanner should show. */
  function findmy(template, adv) {
    const addr = Uint8Array.of(adv[0] | 0xc0, ...adv.slice(1, 6));
    const data = Uint8Array.of(0x4c, 0x00, 0x12, 0x19, 0x00, ...adv.slice(6, 28), adv[0] >> 6, 0x00);
    let t = replaceOnce(template, FM_ADDR, `"bdAddr": "${hex(addr)}"`);
    t = replaceOnce(t, FM_DATA, `"data": "4c00${hex(data.slice(2)).toUpperCase()}"`);
    return { cfg: t, address: colon(addr), typed: colon(addr.slice().reverse()),
             toolData: hex(data.slice(2)).toUpperCase(), raw: "0x1EFF" + hex(data).toUpperCase() };
  }
  function parseHubbleKey(s) {
    s = s.trim();
    let b;
    if (/^[0-9a-fA-F]{32}$/.test(s)) b = fromHex(s.toLowerCase());
    else {
      try { b = fromB64(s); } catch (e) { throw new Error("The key is neither 32 hex characters nor base64."); }
    }
    if (b.length !== 16) throw new Error(`A Hubble key is 16 bytes; this is ${b.length}.`);
    return b;
  }
  /** Hubble .cfg text with the key written in. */
  const hubble = (template, key) => replaceOnce(template, HB_KEY, `"key0": "${hex(key)}"`);
  const safeName = (s) => (s.trim().replace(/[^A-Za-z0-9_-]+/g, "_") || "gantu_tag");

  return { hex, fromHex, b64, fromB64, publicKey, newKeyPair, keysFile, parseAdvKey, findmy, parseHubbleKey,
           hubble, safeName };
})();
if (typeof module !== "undefined") module.exports = GantuCfg;

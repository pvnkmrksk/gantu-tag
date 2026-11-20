# Build guide: from a JLCPCB order to a tag that reports where it's been

Every step for both tags, in order. The same guide, with a key-to-config form, is on the website:
[pvnkmrksk.github.io/gantu-tag/guide.html](https://pvnkmrksk.github.io/gantu-tag/guide.html).

You'll order assembled panels from JLCPCB, fit an antenna wire, load a configuration over four wires and burn it
into the chip, then follow the tag through Apple Find My or Hubble. There's no firmware to write and no fine-pitch
soldering. Budget about €250–300 for the first order (36 tags) and €15–25 for tools you may not have.

1. [Shopping list](#1-shopping-list)
2. [Order the panels from JLCPCB](#2-order-the-panels-from-jlcpcb)
3. [Break out a tag](#3-break-out-a-tag)
4. [Fit the antenna wire](#4-fit-the-antenna-wire)
5. [Make the programming jig](#5-make-the-programming-jig)
6. [Program the tag](#6-program-the-tag)
7. [Finish the tag](#7-finish-the-tag)
8. [Follow it](#8-follow-it)

## 1. Shopping list

| What | Get | Notes |
|---|---|---|
| **The tags** | One JLCPCB order: 2 assembled panels, 20 Hagalu + 16 Irulu | ≈ €250–280 before shipping and VAT (Nov 2026) |
| **USB-to-serial adapter, 3.3 V** | A CP2102 module with pins DTR, RXD, TXD, +5V, GND, 3V3, such as [Waveshare's CP2102 board](https://www.waveshare.com/cp2102-usb-uart-board-type-c.htm) or any generic one | Its 3V3 pin must supply ≥ 100 mA (burning needs up to 50 mA). The generic CP2102 board in the photos burned tags from its own 3V3 pin. **Never 5 V logic.** CH340, CP2104 and FTDI boards set to 3.3 V also work; an FT232R's 3V3OUT is too weak. |
| **Jig** | 4 female-to-female Dupont jumpers, a 2 × 2 block of 2.54 mm male header pins, a rubber band or hair tie | See [step 5](#5-make-the-programming-jig) |
| **Antenna wire** | ≈ 0.1 mm enamelled copper ("magnet wire", ≈ 38 AWG), solderable enamel if you can get it | 31 mm per arm, ≈ 2 mg. Plain thin copper wire also works. |
| **Irulu only** | SR416SW (337) silver-oxide cells (Renata or Maxell); silver conductive epoxy, such as [MG Chemicals 8331D](https://mgchemicals.com/products/adhesives/electrically-conductive-adhesives/silver-epoxy/); Kapton tape; 0.2 mm tinned copper wire | Buy **SR**, not LR/AG (alkaline). Never solder to a cell. |
| **Tools** | Fine-tip soldering iron, flux, tweezers, scalpel, flush cutter, fine sandpaper, thin clear epoxy | |
| **Software** | InPlay's **NanoBeacon Config Tool** (Windows, macOS, Linux) from [inplay-tech.com](https://inplay-tech.com/in100); Python 3 (optional) | |
| **Phone** | nRF Connect (Android or iOS) to see adverts; the Hubble app for Hubble tags; a lux meter app for Hagalu | iOS hides BLE addresses; InPlay's NanoBeacon scanner app shows them |

## 2. Order the panels from JLCPCB

1. Download [`order/insect_tag_v8.3_jlc_order.zip`](../order/insect_tag_v8.3_jlc_order.zip) and unzip it. It holds
   the Gerber zip, the BOM and the placement (CPL) file that went into the first order.
2. At [jlcpcb.com](https://jlcpcb.com), start an order and upload `insect_tag_v8_combined_panel_gerbers.zip`.
3. Set the PCB options:

   | Setting | Value |
   |---|---|
   | Layers, material | 2, FR-4 |
   | Different Design in Panel | **2** |
   | Delivery format | **Panel by Customer** (frame, tooling holes and fiducials are in the Gerbers) |
   | PCB qty | 5 (the minimum) |
   | **Thickness** | **0.6 mm** |
   | Surface finish | ENIG recommended (LeadFree HASL also works) |
   | Mark on PCB | Specify a location (the `JLCJLCJLCJLC` text on the bottom rail) |
   | Via covering | Tented |
   | Everything else | Default |

4. Turn on **PCB Assembly**: **Standard** (Economic only takes 0.8–1.6 mm boards), top side, **2** panels, tooling
   holes added by customer, confirm parts placement: yes.
5. Upload `insect_tag_v8_combined_panel_bom.csv` as the BOM and `insect_tag_v8_combined_panel_pos.csv` as the CPL.
   Check stock: the IN100 (`C6062024`) and the TPS3831 (`C2066667`) were the tight ones.
6. **Check the placement preview** before paying:
   - U1 (IN100): the pin-1 dot sits next to the crystal.
   - Y1 (crystal): a 90° rotation shorts it to GND and kills the tag; 180° is harmless.
   - U2 (TPS3831, Hagalu S tags only): pin-1 dot at the upper left.
   - D2 (RB751, Hagalu S tags only): cathode bar towards C5.
   - Photodiodes: pad 1 is the cathode, marked by the silk bar; the middle row of each 2 × 3 block is turned 180°.
   - The bottom row of the panel is turned 180°, so its marks are too. Fix offsets in JLC's preview, not in the files.
7. Pay. The first order took 13 days from order to delivery. You get 2 assembled panels (8 Hagalu S6, 8 S6L,
   4 N6, 8 Irulu V1, 8 V2) and 3 bare ones. The variant is printed on each tag's underside.

More detail and the reasoning: [`order/README.md`](../order/README.md) and [`panel/README.md`](../panel/README.md).

## 3. Break out a tag

<img src="photos/panel_assembled_2026-11-19.jpg" width="360" alt="An assembled panel from JLCPCB">

- **Keep the tail on**: it carries the four programming holes.
- **Don't snap the body out.** Cut its tab with a flush cutter or scalpel from the panel side while supporting the
  tag, then sand the nub. C1 and U2 sit 0.2 mm from the long edges.
- The tail's tabs are wide; snap or cut those however you like.

## 4. Fit the antenna wire

The antenna is one or two straight wires, each **31 mm** (a quarter wave at 2.44 GHz).

| Hagalu (underside) | Irulu (top) |
|---|---|
| <img src="../hagalu/docs/pcb_3d_bottom.png" width="260" alt="Hagalu underside with the ANT and GND edge pads"> | <img src="../irulu/docs/pcb_3d_top.png" width="260" alt="Irulu top with the ANT rim pad"> |
| **ANT** (AE1): the 1.2 × 1.0 mm pad on the right edge, level with the IN100. **GND** (AE2): the same size, lower left. | **ANT** (AE1): the 1.2 × 0.9 mm pad on the upper-right rim, **ANT** printed below it. **GND** (AE2): the slim pad on the lower-left rim, about 8 o'clock. |

1. Cut 31 mm of ≈ 0.1 mm enamelled copper. Strip the last 1–2 mm (scrape it, or melt solderable enamel off with a
   hot iron) and tin it.
2. Add flux to the **ANT** pad, lay the wire flat along it so it leaves over the edge, and reflow.
3. For a **dipole** (recommended on Hagalu, and on Irulu for Hubble or long range): a second 31 mm wire on the
   **GND** pad, leaving the opposite way. Never join the two wires.
4. Keep the joints low: Hagalu's underside faces the insect.

**Which wire:** thin enamelled copper is light (≈ 2.2 mg per 31 mm at 0.1 mm, ≈ 8.7 mg at 0.2 mm) and easy to
solder, but it kinks. Superelastic nitinol wire, glued on with silver epoxy, is on the
[roadmap](roadmap.md#antenna-and-joints-without-solder).

## 5. Make the programming jig

| The jig on a CP2102 adapter | Four header pins held square by a rubber band |
|---|---|
| <img src="photos/jig_cp2102_dupont_2026-11-20.jpg" width="320" alt="A CP2102 USB-serial adapter with four jumper wires ending in a block of four header pins held by an elastic band, next to a cut-off programming tail"> | <img src="photos/jig_pins_rubber_band_2026-11-20.jpg" width="320" alt="Close-up of the four pins and the tail's four holes marked G, R, T and +"> |

The tail has four plated holes on a 2.54 mm grid, 0.8 mm drill. A square 0.64 mm header pin is ≈ 0.9 mm across its
corners, so it wedges into the hole and holds by itself. No pogo pins, no clamp.

1. Push a **2 × 2 block of male header pins** into the female ends of **four jumper wires**. Two 2-pin pieces snapped
   off a strip work.
2. **Wrap a rubber band** tightly round the four jumper housings so they can't splay. The pins now sit rigidly on
   the same 2.54 mm grid as the holes.
3. Connect the other ends to the adapter. The letters are printed next to each hole on the tail, and the **square
   hole is G**:

   | Tail | Adapter | |
   |---|---|---|
   | **G** (square) | GND | |
   | **+** | **3V3** | never +5V |
   | **R** (into the IN100) | TXD | |
   | **T** (out of the IN100) | RXD | |

   G and T sit diagonally opposite each other, as do R and +. Leave DTR and +5V empty. If the tool can't find the
   chip, swap R and T: that's the usual mistake.
4. **Seat the jig in the tag first, then plug the adapter into USB.** All four pins then make contact before
   anything is powered, so the serial line can't back-power the chip. To power-cycle, unplug the USB, not the jig.

## 6. Program the tag

The IN100 runs no firmware. A configuration (address, advert, interval, TX power, key) goes in over the serial
port: first into RAM, where it's lost at power-off, then **once** into one-time-programmable memory (OTP).

**Hagalu: program in dim light** (the photodiodes would otherwise fight the adapter). **Irulu: program before the
cell goes on**, and never connect the jig once a cell is fitted: it would drive 3.3 V into the cell.

### 6.1 Make the key and the config

Pick a network. The hardware is the same; only the configuration differs.

| | Apple Find My (OpenHaystack) | Hubble Network |
|---|---|---|
| Who hears it | Any nearby iPhone, through Apple's Find My network | Phones running a Hubble-enabled app, and Hubble's gateways |
| On a walk through town (20 Nov 2026) | Dense: well over a hundred sightings in an afternoon | Sparse: 25 packets |
| Location | The relaying iPhone's estimate: ±73–102 m in our reports | The relaying phone's GPS fix (±2.4 m in the example) |
| Sensor data | None: the whole advert is the key | 7 encrypted bytes: VCC, temperature, advert count |
| Cost | Free; needs an Apple ID to fetch reports | Hubble account; free starter tier |
| Key | You make it | Hubble issues it when you register the device |

**Get the key:**

- **Find My:** `python3 tools/new_findmy_tag.py hagalu_03` makes a key pair and writes `hagalu_03.keys` and
  `hagalu_03.findmy.cfg` to `~/gantu-keys/` (or `$GANTU_KEYS`). Keep the private key: it's the only way to
  decrypt the reports. Already have a key from OpenHaystack? Add `--adv-key <base64 advertisement key>`.
- **Hubble:** in the Hubble dashboard, register a device with encryption **AES-128-EAX**, counter mode
  **DEVICE_UPTIME** and period exponent **15**, and name it after the tag. Copy its key, then run
  `python3 tools/new_hubble_tag.py hagalu_002` and paste the key when asked. It writes `hagalu_002.hubble.key` and
  `hagalu_002.hubble.cfg`. If the three settings don't match, Hubble drops the packets silently.

**No Python?** The website's [configure form](https://pvnkmrksk.github.io/gantu-tag/guide.html#configure) takes
the key and gives you the finished `.cfg`, in your browser. Or edit a [template](../configs/) by hand: for Hubble
that's one line, `"key0"`.

The configs are 0 dBm, 1 Mbps, all three advertising channels, XO cap code 8; Find My every 3 s, Hubble every 4 s.

### 6.2 Test it in RAM

1. Open the NanoBeacon Config Tool and **Load** your `.cfg`. Leave the advertising data format on **Custom**
   (the tool's own "Hubble" format sends the payload unencrypted).
2. Seat the jig in the tag and plug the adapter in: a **fresh power-up**.
3. **Probe**, pick the port (`/dev/cu.usbserial-…` on a Mac, `COM…` on Windows) and **Connect** straight away.
4. **Run in RAM.** The tag starts advertising.
5. Check it on the phone:
   - **Find My:** nRF Connect shows manufacturer data `0x004C` with raw data starting `1EFF4C00121900`, no flags.
     The script prints the exact bytes and the address to expect.
   - **Hubble:** service data for UUID `0xFCA6`. Open the Hubble app near the tag. To check it yourself, copy the
     service data from nRF Connect and run `python3 tools/hubble_decode.py ~/gantu-keys/hagalu_002.hubble.key <hex>`.
     It checks the rotating ID against the key and prints VCC, temperature and the advert count.

**One RAM load per power-up.** Once a configuration runs, the chip stops answering the tool: Connect fails, or Run
in RAM reports Done and changes nothing. To load another one, Load it in the tool, unplug and replug the USB,
Connect straight away, and Run in RAM once.

### 6.3 Burn it

When the RAM test works: power-cycle, Connect straight away, and **Program** (burn) instead of Run in RAM. **This
can be done only once per tag.** Write down which key went on which tag ([`docs/tags.md`](tags.md) is the record
for the bench tags). The Config Tool keeps a copy of what it sent in its log folder (`nano_beacon_config.cfg`):
compare it with your file.

Unplug: the tag now runs on its own. A Hagalu advertises only in light (steady from about 1.9 klx; a desk lamp at
20–30 cm, daylight, or a well-lit shop). An Irulu advertises once its cell is fitted.

## 7. Finish the tag

**Hagalu**

1. Cut the tail at **CUT**: score both faces with a scalpel and snap, or file through. Side cutters can smear the
   VCC and GND tracks together.
2. Clean off the flux, and seal the cut edge with a dot of epoxy.
3. Coat the photodiodes thinly with clear, unpigmented epoxy. Keep all six equally lit: the most shaded one sets
   the current.
4. Store tags in the dark.

**Irulu**

1. V2 only: bridge the **OFF** jumper on the tail with solder; the tag will stay silent until you cut the tail.
2. Optional: a Kapton washer (≈ Ø 7 mm, Ø 2 mm hole) on the underside, its hole over the round − pad.
3. A **small** dab of silver epoxy on the − pad; seat the cell **− cap down**, centred on the printed ring. Epoxy
   that bridges cap and can shorts the cell.
4. A short 0.2 mm tinned wire from the **+** pad to the can's side wall, fixed with silver epoxy. **Never solder to
   the cell.** MG 8331D cures in about 6 h at room temperature, or 10 min at 65 °C.
5. Check: + and G on the tail read the cell voltage. V1 now advertises; V2 is silent.
6. V2 in the field: cut the tail at **CUT** (scalpel, not side cutters: the cell is live) and seal the edge.
7. Encapsulate in ordinary epoxy, leaving the antenna free beyond the first millimetre.

Full details: [`hagalu/README.md`](../hagalu/README.md#hand-assembly) and
[`irulu/README.md`](../irulu/README.md#hand-assembly).

## 8. Follow it

The [Gantu dashboard](dashboard.md) collects both networks on one Pi or laptop, with a map and saved history
for each tag and decoded readings from Hubble. The setup guide shows how to add your tags and leave a Pi
collecting when you turn your laptop off.

**Find My.** Nearby iPhones report the tag's position to Apple, encrypted to your key. Fetch and decrypt the
reports with the private key from `<name>.keys`, using an OpenHaystack-compatible fetcher such as
[FindMy.py](https://github.com/malmeloo/FindMy.py) or [macless-haystack](https://github.com/dchristl/macless-haystack)
(Docker; it runs on a Raspberry Pi). Both need an Apple ID.

**Hubble.** Packets show up in the Hubble app and dashboard. Hubble's packets API and webhooks return each packet
with the relay's location and the payload already decrypted, as base64; `parse_sensors()` in
[`tools/hubble_decode.py`](../tools/hubble_decode.py) turns it into VCC, temperature and advert count.

What it looked like on a walk on 20 Nov 2026, with gantu_S6_01 on Find My and Hagalu-002 on Hubble, both Hagalu
tags running on light only. The cluster of close points is inside a supermarket, under ordinary shop lighting.

| Find My: the track | Find My: sightings | Hubble: one packet with its payload |
|---|---|---|
| <img src="photos/walk_findmy_track_2026-11-20.jpg" width="260" alt="Map of Find My sightings of a Hagalu tag, coloured from oldest to newest"> | <img src="photos/walk_findmy_sightings_2026-11-20.jpg" width="260" alt="Dashboard listing 143 Find My sightings in view and 220 saved"> | <img src="photos/walk_hubble_payload_2026-11-20.jpg" width="260" alt="A Hubble packet decoded as 1.562 V, 28.45 degrees C, 0 adverts, with the relay's GPS fix"> |

Hubble's payload from a tag running on light: **1.562 V, 22–28 °C, advert count 0** in every packet checked. The count and
the uptime counter restart before each advert at this supply voltage, so on Hagalu they carry no information, and
the rotating ID stays at its first value (Hubble still decodes it). See the
[roadmap](roadmap.md#stage-0-bench-work-on-the-v83-boards-now).

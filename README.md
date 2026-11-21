<p align="center"><img src="docs/logo/gantu.svg" width="140" alt="gantu-tag logo: a trefoil knot"></p>

<h1 align="center">gantu-tag · ಗಂಟು</h1>

<p align="center"><b>Open, tiny Bluetooth LE tracking tags for insects that anyone can order from JLCPCB.</b></p>

*Gantu* (ಗಂಟು, said *gun-two*) is Kannada for a knot, for someone who clings on and goes wherever you go, and for
a node.
[More about the name](#about-the-name).

**Website:** https://pvnkmrksk.github.io/gantu-tag/ · **Build guide:** [step by step](docs/guide.md)
([on the website](https://pvnkmrksk.github.io/gantu-tag/guide.html), with a form that turns your key into a config) ·
**Dashboard:** [Gantumoote](https://github.com/pvnkmrksk/gantumoote), self-hosted on a Pi or laptop

These are **early pilots**. The first panels were ordered on 6 November 2026 and arrived assembled on 19 November;
bench testing has started. **First result, the same evening:** a Hagalu S6, configured over UART and run from RAM
with a plain copper antenna, was picked up by passing iPhones and reported through Apple Find My three times in
20 minutes (±76–102 m). It advertised steadily from about 1.9 klx, and weighs **0.242 g** with its wire antenna
(tail cut, no epoxy). Treat every other number here as a design estimate until bring-up is complete.

**First walk, 20 November:** two burned Hagalu tags, running on light alone, went for a walk through town: one on
Apple Find My, one on Hubble. Both were reported, including from inside a supermarket under ordinary shop lighting.
Find My gave well over a hundred sightings in the afternoon; Hubble gave fewer (25 packets), but each one carried the
relaying phone's GPS fix and the tag's own encrypted payload: supply voltage and temperature.

| Find My: the track | Find My: sightings | Hubble: a packet and its decoded payload |
|---|---|---|
| <img src="docs/photos/walk_findmy_track_2026-11-20.jpg" width="260" alt="Map of Find My sightings of a Hagalu tag, coloured from oldest to newest"> | <img src="docs/photos/walk_findmy_sightings_2026-11-20.jpg" width="260" alt="Dashboard listing 143 Find My sightings in view and 220 saved"> | <img src="docs/photos/walk_hubble_payload_2026-11-20.jpg" width="260" alt="A Hubble packet decoded as 1.562 V, 28.45 degrees C, 0 adverts, with the relay's GPS fix"> |

<p align="center"><img src="docs/photos/panel_assembled_2026-11-19.jpg" width="560" alt="An assembled gantu-tag panel from JLCPCB, held in hand"></p>

| Weighed: 0.242 g | Advertising Find My under 1.7 klx |
|---|---|
| <img src="docs/photos/hagalu_s6_on_scale_242mg_2026-11-19.jpg" width="280" alt="Hagalu S6 with its wire antenna on a 1 mg scale, reading 0.242 g"> | <img src="docs/photos/hagalu_s6_findmy_advert_1704lx_2026-11-19.jpg" width="280" alt="nRF Connect showing a Find My advert from the tag at -57 dBm, with a second phone reading 1704 lx"> |

## The two tags

<p align="center"><img src="hagalu/docs/pcb_3d_top.png" width="300" alt="Hagalu Gantu, solar tag"> <img src="irulu/docs/pcb_3d_top.png" width="300" alt="Irulu Gantu, battery tag"></p>

| | **Hagalu Gantu** · ಹಗಲು ಗಂಟು | **Irulu Gantu** · ಇರುಳು ಗಂಟು |
|---|---|---|
| Power | Six photodiodes charge a 100 µF capacitor; no battery | A silver-oxide button cell (337, 364 or 377) |
| When it runs | **In light only**, in bursts as the capacitor fills | Continuously until the cell is flat (≈ 57 days on a 337 at a 3 s interval) |
| Size (after cutting the tail) | 6.4 × 12.55 mm | Ø 7.2 mm |
| Mass (0.6 mm board) | **0.242 g measured** (S6 with wire, no epoxy; estimate was 0.19–0.21 g) | ≈ 0.12 g without the cell, ≈ 0.25 g with a 337 (estimate) |
| **Cost per tag** (approx.) | **≈ €7** | **≈ €2.30** + a button cell |
| Start-up | On S6/S6L a supervisor starts the radio once the capacitor holds a burst; N6 has none | Fit the cell (V1), or cut the tail (V2) |
| Pilot variants on the panel | S6, S6L, N6 | V1, V2 |
| Design files | [`hagalu/`](hagalu/) | [`irulu/`](irulu/) |

### Renders

KiCad 10 renders of the v8.3 boards as ordered. Top: parts side. Bottom: the antenna pads on Hagalu, and the cell
pads on Irulu.

| | Top | Bottom |
|---|---|---|
| **Hagalu Gantu** | <img src="hagalu/docs/pcb_3d_top.png" width="260" alt="Hagalu top"> | <img src="hagalu/docs/pcb_3d_bottom.png" width="260" alt="Hagalu bottom"> |
| **Irulu Gantu** | <img src="irulu/docs/pcb_3d_top.png" width="260" alt="Irulu top"> | <img src="irulu/docs/pcb_3d_bottom.png" width="260" alt="Irulu bottom"> |

The JLC panel (94.9 × 71.1 mm, 0.6 mm), with 10 Hagalu and 8 Irulu tags on each panel:

<p align="center"><img src="panel/docs/panel_top.png" width="640" alt="Combined panel, top"></p>

The pilot variant names (S6, S6L, N6, V1, V2) only mark the start-circuit options under test. They'll be narrowed
down once the first tags are on the bench.

## Approach

The tag doesn't carry a GPS or a receiver. It only **broadcasts a Bluetooth LE advert every few seconds**, and phones
or gateways that belong to a large existing network hear it and report where they were. You then fetch those
reports.

- **One chip, configured rather than programmed.** Both tags use the InPlay
  [IN100 NanoBeacon](https://inplay-tech.com/in100). It runs no firmware: you load a configuration over its UART
  (address, advert bytes, interval, TX power), test it in RAM, then burn it once into the chip's one-time-programmable
  memory. That keeps the tag down to the chip, a crystal and a few capacitors.
- **Two networks, the same hardware.** Which network a tag joins is decided only by what you burn into it:
  - **Apple Find My** via [OpenHaystack](https://github.com/seemoo-lab/openhaystack): the tag sends a fixed-key
    Find My advert, nearby iPhones relay its position to Apple, and you decrypt the reports with your private key.
    No Apple hardware is needed on the tag side, and it costs nothing per tag.
  - **[Hubble Network](https://hubble.com)**: the IN100 is one of Hubble's supported chips, and its adverts are picked
    up by Hubble's terrestrial network of phones and gateways and, as its next satellites arrive, from orbit. Hubble
    is a paid service with a free starter tier.
- **Built by JLCPCB, finished by hand.** Every part is placed by JLCPCB's assembly service from its own stock, on a
  2-layer 0.6 mm board. You add only the antenna wire, the cell (Irulu) and epoxy.
- **Started by cutting.** Each tag carries its programming pads on a tail. Like commercial bat and insect tags, you
  program it, then cut the tail off; on Irulu V2 the cut is also what switches it on.
- **Pilots before a batch.** The first panel carries several population variants of each tag (S6/S6L/N6 and V1/V2),
  so one order shows which start circuit works before anyone orders in bulk.

## Build your own

The [build guide](docs/guide.md) walks through every step, with photos. In short:

1. **Order** the files in [`order/`](order/) from JLCPCB: 0.6 mm, Panel by Customer, Standard PCBA, 2 assembled
   panels. One order gives 20 Hagalu and 16 Irulu tags.
2. **Fit the antenna:** a 31 mm, ≈ 0.1 mm wire on the **ANT** pad, and a second one on **GND** for a dipole.
3. **Make the jig:** four jumper wires, a 2 × 2 block of header pins and a rubber band. The pins wedge into the
   tail's four 0.8 mm holes and hold by themselves.
4. **Make the config:** take a template from [`configs/`](configs/) and add your key, from Find My (you generate it)
   or Hubble (it issues one). Use `tools/new_findmy_tag.py` or `tools/new_hubble_tag.py`, or the website's form.
5. **Program:** InPlay's NanoBeacon Config Tool. Test in RAM, then burn the one-time-programmable memory
   ([details](docs/programming.md)).
6. **Finish:** fit the cell on Irulu, cut the tail, coat in epoxy. Then follow the tag through Find My or Hubble.

| The jig | Wiring: tail → 3.3 V USB-serial adapter |
|---|---|
| <img src="docs/photos/jig_pins_rubber_band_2026-11-20.jpg" width="300" alt="Four header pins in jumper wires, held square by an elastic band, next to a tail with holes marked G, R, T and +"> | **G** (square hole) → GND<br>**+** → 3V3 (never 5 V)<br>**R** → TXD<br>**T** → RXD<br><br>Seat the jig first, then plug in the USB. |

## Follow your tags

[Gantumoote](https://github.com/pvnkmrksk/gantumoote), the self-hosted dashboard in its own repository, is the map we used for the first walk. Run it on a laptop or leave
it collecting on a Raspberry Pi. It handles Find My and Hubble in the same device list, including voltage,
temperature and advert count from the Gantu Hubble payload. Each tag keeps its own history. Your keys, history
and logs stay on the host. A Pi can start collecting at boot and keep the same HTTPS address through a named tunnel.

## Roadmap

Lighter first, then simpler, then cheaper. The full plan, with mass targets, is in [`docs/roadmap.md`](docs/roadmap.md).

| Stage | What | Hagalu | Irulu (with a 337) |
|---|---|---|---|
| **Now** | Bench work on the v8.3 pilots: mass split, Irulu bring-up, S6L/N6, a smaller C1, range; nitinol antenna wire and silver-epoxy joints instead of solder | 0.242 g measured | ≈ 0.25 g |
| **v9** | Polyimide flex, antenna as a trace on a flex tail, thinner copper, 47 µF C1 if it tests well | ≈ 0.13–0.16 g | ≈ 0.19–0.20 g |
| **v10** | IN100 in WLCSP (1.1 × 2.0 mm), 0201 parts; Irulu no bigger than its cell | ≈ 0.05–0.07 g | ≈ 0.16–0.17 g |

On Irulu the 0.13 g cell is the floor; everything else can shrink to ≈ 0.03–0.04 g.

## Repository map

| Folder | What's in it |
|---|---|
| [`hagalu/`](hagalu/) | Solar tag: KiCad project, the Python that generates it (`tools/design.py`), solar simulation, renders, review |
| [`irulu/`](irulu/) | Battery tag: KiCad project, generator, burst simulation, renders, review |
| [`panel/`](panel/) | The combined 0.6 mm JLC panel (KiKit layout, mixed-variant BOM/CPL) and its ordering README |
| [`order/`](order/) | The exact files sent to JLCPCB, with a checksum |
| [`configs/`](configs/) | Find My and Hubble config templates for InPlay's Config Tool: add your key |
| [`tools/`](tools/) | Make a tag's key and config (`new_findmy_tag.py`, `new_hubble_tag.py`); decode a Hubble advert (`hubble_decode.py`) |
| [`docs/`](docs/) | [Build guide](docs/guide.md), [programming](docs/programming.md), [roadmap](docs/roadmap.md), [tag records](docs/tags.md), the v8 handover and build notes, photos, the logo |
| [`site/`](site/) | The website ([publish it](site/publish.sh) to the `gh-pages` branch) |

## History

Every revision is a commit, dated when it was made. The commit that closes each version:

| Version | What changed |
|---|---|
| [`v4`](https://github.com/pvnkmrksk/gantu-tag/tree/ffad947) | 6.4 mm round tag on a 0.6 mm board, printed antenna arm, cut-off programming tab |
| [`v5`](https://github.com/pvnkmrksk/gantu-tag/tree/3f6ccb6) | 8 mm tag with a 30 mm wire antenna; all parts on the top side, cell underneath |
| [`v6`](https://github.com/pvnkmrksk/gantu-tag/tree/cb1977e) | 7 mm tag with a Blu Bat-style **cut-to-start tail** (superseded: pour and decoupling faults, don't order) |
| [`v7`](https://github.com/pvnkmrksk/gantu-tag/tree/bdc53f7) | Fixes v6; any button cell; five population variants on one test panel |
| [`v8.3`](https://github.com/pvnkmrksk/gantu-tag/tree/761deb4) | Split into **Hagalu** (solar) and **Irulu** (battery) on one combined 0.6 mm panel. **This is what was ordered** |

Before v8 there was only the battery tag, so its history lives in `irulu/`. Click a version to browse it, or
`git checkout cb1977e` for v6, for example.

## Bill of materials and cost

Per-tag parts lists with LCSC numbers are on the [website](https://pvnkmrksk.github.io/gantu-tag/#bom); the full
panel BOM is [`panel/fab/jlcpcb_panel/insect_tag_v8_combined_panel_bom.csv`](panel/fab/jlcpcb_panel/insect_tag_v8_combined_panel_bom.csv).
Approximate cost per tag, parts and JLC placement, at November 2026 prices:

| | Per tag |
|---|---|
| **Hagalu Gantu** (solar) | **≈ €7** |
| **Irulu Gantu** (button cell) | **≈ €2.30**, plus the cell you fit yourself |

Each order also carries one-off fees of roughly €100 (setup, stencil, extended-part fees, bare boards), which you
spread over however many tags you order. The first order (5 bare panels, 2 assembled, 36 tags) came to about
**€250–280 before shipping and VAT**. Most of the cost is the IN100 (≈ $2.60) and, on Hagalu, the six photodiodes
(≈ $0.87 each). The JLC cart is the real number.

## Licence

**Open, and it has to stay open.** You can use, change, build, sell and share all of it, commercially or not, on two
conditions that pass on to everything made from it:

1. **Credit the author.** Keep the [`NOTICE`](NOTICE) file and credit the work wherever you publish, show or sell
   it or anything made from it:

   > Based on gantu-tag by Pavan Kumar Kaushik, https://github.com/pvnkmrksk/gantu-tag

2. **Share alike.** Release what you make from it under the same licence, with its source.

| What | Licence |
|---|---|
| **Hardware:** KiCad projects, Gerbers, BOM and placement files, the panel, the order files, the tag configs in `configs/` | [CERN-OHL-S-2.0](LICENSE), strongly reciprocal: boards and tags made from the design count too |
| **Documentation and media:** the docs, photos, renders, PDFs, the logo, the website's text and images | [CC BY-SA 4.0](LICENSE-DOCS) |
| **Software:** `tools/`, `*/tools/`, the review scripts, `docs/logo/make_logo.py`, the website's code | [AGPL-3.0-or-later](LICENSE-CODE): also covers modified copies run as a web service. The dashboard, [Gantumoote](https://github.com/pvnkmrksk/gantumoote), is AGPL too |

Two conditions in [`NOTICE`](NOTICE) make the credit concrete: anyone who sells or hands out tags made from the
design must include the source link and the credit line in the packaging or documentation, and modified software
must keep the credit in its source and in its legal notices.

Versions up to commit `53f775e` (20 November 2026) were published under CC BY 4.0 and MIT, and copies of those keep
those terms; everything after is under the licences above. The circuits follow InPlay's IN100 datasheet and the
component values on SparkFun's NanoBeacon board; no SparkFun design files are included. There's no warranty: you
build and use these at your own risk.

## About the name

**Gantu** (ಗಂಟು, *gun-two*, /ɡəɳʈu/) works on three levels:

- **A knot.** The tag is tied onto the animal.
- **Clinging on.** Colloquially, someone who is *gantu* to you sticks to you and goes wherever you go, as if the two of
  you were knotted together. That's the tag and its insect.
- **A node,** as on a plant stem or in a network. The tag is found as a node heard by a mesh of phones and gateways.

**Hagalu** (ಹಗಲು, *huh-guh-loo*, /ɦəɡəlu/, day) and **Irulu** (ಇರುಳು, *ih-roo-loo*, /iruɭu/, night) name how each
tag works: Hagalu runs on daylight, Irulu runs on its cell through the night as well.

The *ṇṭ* in gantu is retroflex (tongue curled back), as is the *ḷ* in irulu. The logo is one thread tied in a trefoil
knot, shading from turmeric ochre into indigo.

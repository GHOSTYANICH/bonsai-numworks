<div align="center">

<h1>🌳 bonsai.py</h1>

<p><strong>A generative ASCII bonsai for the NumWorks graphing calculator</strong></p>

<p>Inspired by <a href="https://gitlab.com/jallbrit/cbonsai">cbonsai</a> · Written in Python · No installation required</p>

<img src="https://img.shields.io/badge/platform-NumWorks-4B6BFB?style=flat-square" alt="Platform: NumWorks" />
<img src="https://img.shields.io/badge/Python-Epsilon-3776AB?style=flat-square&amp;logo=python&amp;logoColor=white" alt="Python: Epsilon" />
<img src="https://img.shields.io/badge/license-MIT-2EA44F?style=flat-square" alt="License: MIT" />

</div>

```text
                               &&&
                              &&&&
                         &&&&&&|&
             &_&&  \_/| &&\&&/&/ &
             &&  \\  \_  &&/|/&
            && &&&   /| /|/~&\& _&
           &  &&//   \&|/  & \/|&&
              &   //  &\/_/  &/| &
                    /&&&&&//_&&_&&
                      /&\    &&
                      /~&
               (---./~~\.---)
                (           )
                 (_________)
```

Every run grows a new tree, one branch at a time, directly on the calculator’s screen.

> [!NOTE]
> `bonsai.py` uses only `kandinsky`, `ion`, and `random` — all included with Epsilon. There are no extra libraries to install.

## Contents

- [Install](#install)
- [Controls](#controls)
- [Options](#options)
- [How it grows](#how-it-grows)
- [Tweaking](#tweaking)
- [Compatibility](#compatibility)
- [Credits](#credits)

## Install

1. Open [my.numworks.com/python](https://my.numworks.com/python/) and go to **My scripts**.
2. Select **New script**, name it `bonsai.py`, then paste in the contents of [`bonsai.py`](bonsai.py).
3. Select **Send to calculator**.
4. On the calculator, open **Python** → `bonsai` → **EXE**.

## Controls

| Key | Action |
|:---:|---|
| `UP` / `DOWN` | Move between menu lines |
| `LEFT` / `RIGHT` | Change the selected value |
| `OK` | Grow a tree; press again while it grows to finish instantly |
| `DEL` | Go back, stop the auto loop, or quit |

## Options

```text
Theme  < Dark >
Leaves < Green >
Size   < Tiny >
Auto   < Off >
[ Grow ]
```

| Option | Choices | Description |
|---|---|---|
| **Theme** | `Dark`, `Light` | Repaints the menu immediately, so you can preview the theme before growing. |
| **Leaves** | `Green`, `Sakura`, `Autumn`, `Random` | `Sakura` is pink; `Autumn` is orange/red; `Random` selects a palette for each tree. Every palette has shades for both themes. |
| **Size** | `Tiny`, `Small`, `Medium`, `Big` | Changes the amount of drawing, not the character size. Epsilon has only two fixed fonts. |
| **Auto** | `Off`, `Instant`, `2 sec`, `5 sec` | Sets how long a finished tree remains on screen before the next one begins. `Instant` chains trees together. |

### Size guide

| Size | Trunk life | Branches | Width | Height | Step delay |
|:---|---:|---:|---:|---:|---:|
| Tiny | 13 | 4 | ±9 cols | 7 rows | 40 ms |
| Small | 15 | 5 | ±12 cols | 9 rows | 50 ms |
| Medium | 19 | 7 | ±15 cols | 10 rows | 30 ms |
| Big | 26 | 9 | ±20 cols | Full screen | 20 ms |

## How it grows

The branching model is a Python reimplementation of cbonsai, adapted for NumWorks’ 45 × 15 character display instead of an 80 × 24 terminal.

- **A natural, leaning trunk.** The trunk holds a direction for several steps before swinging back, creating an S-curve. Two-column sideways moves use `_`, `/`, or `\` bridges so the tree stays connected.
- **A guaranteed trunk.** The tree must climb a minimum number of rows before it can turn into foliage, avoiding a leaf-heavy blob at the pot.
- **Branches seek open space.** The canvas is divided into 3 × 2 zones. New branches aim for the emptiest zone, including sideways or downward, then grow freely once there. This keeps the canopy balanced instead of crowding the top centre.

Growth is iterative, using an explicit branch stack rather than recursion, so it stays within MicroPython’s stack limits.

## Tweaking

The main controls live near the top of [`bonsai.py`](bonsai.py):

| Setting | What to change |
|---|---|
| `SIZES` | One tuple per size: `(life, mult, shoots, shoot bonus, half width, min trunk, max height, delay)`. Lower `mult` makes denser branching. Add a tuple to add a menu size; keep the `% 4` in `menu()` aligned with the new total. |
| `ZX`, `ZY` | Zone-grid dimensions. For example, `4, 3` creates twelve zones and a denser tree; increase the branch count in `SIZES` to suit. |
| `DARK`, `LIGHT` | Theme colours, including the three `leafsets` palettes. |
| `AUTO_WAIT` | Delays used by the **Auto** option. |
| `MSGS` | Short messages shown in the on-screen box. |

## Compatibility

- Text is ASCII-only: Epsilon’s font does not include Cyrillic, and unsupported characters appear as boxes.
- Older Epsilon releases without the small font are supported. The script detects this at launch and falls back to a 32 × 12 grid with a shorter tree.

## Credits

Branch behaviour is based on [cbonsai](https://gitlab.com/jallbrit/cbonsai) by John Allbritten, released under GPL-3.0. This is an independent Python reimplementation for NumWorks, released under the [MIT License](LICENSE).
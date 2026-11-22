# Sunday 22 November 2026 — The World in One Picture

[![make.fun bounty](https://img.shields.io/badge/make.fun-news--image--20261122-blue)](https://make.fun/bounty/news-image-20261122)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)

Entry for the [make.fun news-image-20261122 bounty](https://make.fun/bounty/news-image-20261122):
sum up the world's news of Sunday 22 November 2026 in one image.

## The picture

A one-page newspaper front page, drawn from scratch by `draw.py`
(Pillow, procedural art — no photos, no licensed images):

- **Sunday 22 November 2026** as the giant serif headline.
- Three hero stories: Iran's strikes on US bases in the Gulf, Mexico's
  capture of 'El Chapo Isidro', and the COP31 deadlock in Antalya.
- The day in numbers (200 nations at COP31, 15 militants killed in
  Balochistan, 11 killed in the Mexico operation, Trump's 10%
  credit-card cap, 5,300 DRC Ebola deaths, a 73-year river record),
  a per-region count bar, 10 small cards, a world map
  ("WHERE IT HAPPENED") and a numbered "ALSO ON SUNDAY…" list —
  35 stories in total.
- A red **DATE CHECK** box names the big stories deliberately left
  out because they happened before Sunday: the Trump–Xi–Putin
  Shenzhen summit (19 Nov), the World Court's Myanmar ruling (19 Nov),
  Anthropic's $81.3bn debut (19 Nov), Peru's M6.9 quake (20 Nov),
  Estonia's border decision (20 Nov) and the third Kerch Bridge
  strike (19 Nov).

Every story in the picture happened, or was first reported, on Sunday
22 November 2026. All artwork is original drawings.

## How it runs

`main.py` (Python 3.13, standard library only) copies the
repository-held `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`
(default `/output/entry.png`). The run is byte-identical every time.

To regenerate the picture from scratch:

```sh
python3 draw.py            # writes entry.png (1024x1024, < 1 MiB)
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

## Licence

MIT — see [LICENSE](LICENSE).

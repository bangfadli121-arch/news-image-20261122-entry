#!/usr/bin/env python3
"""news-image-20261122 entrypoint (Python 3.13, standard library only).

The front page was drawn by draw.py (Pillow, run at build time) and is
held in this repository as entry.png. This program copies that image to
the output directory, so the run is byte-identical every time.
"""
import os
import shutil
import sys


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

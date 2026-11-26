#!/usr/bin/env python3
"""Publish this entry's finished artwork.

The front page is the pre-rendered ``entry.png`` sitting beside this
file.  Running this program places an identical copy of that image in
the directory named by the ``MAKEFUN_OUTPUT_DIR`` environment variable,
which is where the make.fun kit expects the entry output to appear.

Nothing is rendered here: the image is committed to the repo as-is, so
what the kit collects is byte-for-byte the image that was verified
before the commit.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def publish() -> int:
    here = Path(__file__).resolve().parent
    artwork = here / "entry.png"

    if not artwork.is_file():
        print(f"error: no entry image next to this script: {artwork}",
              file=sys.stderr)
        return 1

    # Validate the source image before copying: it must be a real PNG,
    # identified by its 8-byte magic header, not just any file named .png.
    with artwork.open("rb") as fh:
        header = fh.read(len(PNG_MAGIC))
    if header != PNG_MAGIC:
        print(f"error: {artwork} is not a PNG image "
              f"(bad magic header: {header!r})", file=sys.stderr)
        return 1

    target = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not target:
        print("error: MAKEFUN_OUTPUT_DIR is not set; run as "
              "MAKEFUN_OUTPUT_DIR=<dir> python3 main.py", file=sys.stderr)
        return 1

    out_dir = Path(target)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / artwork.name
    shutil.copyfile(artwork, out_path)

    if out_path.stat().st_size == 0:
        print(f"error: copied image is empty: {out_path}", file=sys.stderr)
        return 1

    # Confirm the copy is byte-identical to the source: a truncated or
    # corrupted copy must never be handed to the kit as the entry.
    source_hash = sha256_of(artwork)
    copied_hash = sha256_of(out_path)
    if copied_hash != source_hash:
        print(f"error: copied image hash mismatch: source {source_hash} "
              f"!= copy {copied_hash}", file=sys.stderr)
        return 1

    print(f"{out_path} ({out_path.stat().st_size} bytes, "
          f"sha256 {copied_hash})")
    return 0


if __name__ == "__main__":
    raise SystemExit(publish())

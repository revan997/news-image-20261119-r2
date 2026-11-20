#!/usr/bin/env python3
"""news-image-20261119-r2 entry point (STDLIB ONLY).

Copies the pre-rendered entry.png shipped next to this file into the
grading output directory (MAKEFUN_OUTPUT_DIR or /output) and verifies
it is a real PNG. No network, no randomness, no clock.
"""
import hashlib
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1048576
EXPECT_W, EXPECT_H = 1024, 1024


def png_size(data):
    """Width/height from the PNG IHDR chunk (no image library needed)."""
    if len(data) < 33 or data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    if not os.path.isfile(SRC):
        print("ERROR: entry.png missing next to main.py", file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    with open(dst, "rb") as f:
        data = f.read()
    if not data.startswith(PNG_MAGIC):
        print("ERROR: output is not a PNG", file=sys.stderr)
        return 1
    size = png_size(data)
    if size != (EXPECT_W, EXPECT_H):
        print("ERROR: unexpected dimensions %s (want %dx%d)"
              % (size, EXPECT_W, EXPECT_H), file=sys.stderr)
        return 1
    if len(data) > MAX_BYTES:
        print("ERROR: output %d bytes exceeds %d" % (len(data), MAX_BYTES),
              file=sys.stderr)
        return 1
    print("wrote %s (%d bytes, %dx%d, sha256=%s)"
          % (dst, len(data), size[0], size[1],
             hashlib.sha256(data).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())

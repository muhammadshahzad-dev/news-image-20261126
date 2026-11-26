#!/usr/bin/env python3
"""Sum up 26 November 2026's world news in one image.

No input, no network: the six verified stories of the day are baked
into STORIES below, and the program draws a 1600x1000 news poster
(PNG) with them.

Run:   python3 main.py
Out:   world-news-2026-11-26.png -- next to this file, or in
       $MAKEFUN_OUTPUT_DIR when that is set (the grader's sandbox).

Rendering: Pillow when it is available (DejaVu fonts), otherwise a
built-in 5x7 bitmap font plus a pure-stdlib PNG writer, so the
program still runs to completion in a bare Python image. Either way
the layout, the text and the output are identical in structure and
the run is fully deterministic (no randomness, no clock, no I/O
besides the one PNG it writes).
"""

import os
import sys

# ---------------------------------------------------------------- stories
# Six verified top world stories of Thursday 26 November 2026.
# Sources: Economic Times (Kim; Musk), Dunya News (Kyiv; Houthis;
# tariffs), OneTurn (tariffs; Houthis; Kyiv; parade), SCMP (birthright
# block; FedEx), Times of India (parade; Kim), Arab News PK (tariffs).
STORIES = [
    {
        "tag": "TRADE",
        "headline": "World reacts to Trump's new tariffs",
        "summary": "Brazil calls the planned US tariffs 'unacceptable' as "
                   "India faces a 17-25% threat.",
    },
    {
        "tag": "KOREA",
        "headline": "Kim vows to build more nuclear weapons",
        "summary": "North Korea's Kim inspects nuclear sites and pledges a "
                   "bigger arsenal, ignoring Trump's offer to meet.",
    },
    {
        "tag": "UKRAINE",
        "headline": "Russia hits Kyiv; Ukraine strikes back",
        "summary": "Russian ballistic missiles hit Kyiv as Ukraine says it "
                   "struck five jets at a Russian airbase.",
    },
    {
        "tag": "MIDDLE EAST",
        "headline": "Houthis attack Saudi ports and refinery",
        "summary": "Yemen's Houthis claim strikes on Saudi ports and the Ras "
                   "Tanura refinery; Riyadh intercepts missiles.",
    },
    {
        "tag": "NEW YORK",
        "headline": "Storm postpones Macy's Thanksgiving parade",
        "summary": "New York's 100th Thanksgiving parade is postponed for "
                   "the first time as a huge storm hits the city.",
    },
    {
        "tag": "USA",
        "headline": "Judge blocks Trump's birthright order",
        "summary": "A US federal judge blocks the president's new executive "
                   "order curtailing birthright citizenship.",
    },
]

DATE_LINE = "Thursday, 26 November 2026"
OUT_NAME = "world-news-2026-11-26.png"

W, H = 1600, 1000
BG = (14, 26, 43)
PANEL = (23, 41, 63)
GOLD = (212, 175, 55)
WHITE = (245, 247, 250)
GREY = (199, 211, 224)
MUTED = (140, 155, 175)

# ------------------------------------------------------------- text utils
# Everything below is plain ASCII so both renderers agree exactly.


def clean(text):
    """Fold fancy punctuation to ASCII (both renderers are ASCII-only)."""
    return (text.replace("\u2014", "-").replace("\u2013", "-")
                .replace("\u2019", "'").replace("\u2018", "'")
                .replace("\u201c", '"').replace("\u201d", '"')
                .replace("\u2022", "|").replace("\u2026", "..."))


def wrap(text, measure, max_w):
    """Greedy word wrap; measure(s) -> pixel width. Returns line list."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if measure(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------- bitmap 5x7 font
# Classic 5x7 glyphs: each glyph is 7 rows, bit 4 = leftmost pixel.
# Used only when Pillow is unavailable.
FONT_5X7 = {
    " ": (0, 0, 0, 0, 0, 0, 0),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    '"': (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),
    "#": (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "%": (0x18, 0x19, 0x02, 0x04, 0x08, 0x13, 0x18),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "*": (0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    "-": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "<": (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    "=": (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    ">": (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "@": (0x0E, 0x11, 0x01, 0x0D, 0x15, 0x15, 0x0E),
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x01, 0x01, 0x01, 0x01, 0x01, 0x11, 0x0E),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "[": (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    "\\": (0x10, 0x08, 0x08, 0x04, 0x02, 0x02, 0x01),
    "]": (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    "^": (0x04, 0x0A, 0x11, 0, 0, 0, 0),
    "_": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F),
    "`": (0x08, 0x04, 0x02, 0, 0, 0, 0),
    "a": (0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F),
    "b": (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x1E),
    "c": (0x00, 0x00, 0x0E, 0x11, 0x10, 0x11, 0x0E),
    "d": (0x01, 0x01, 0x0F, 0x11, 0x11, 0x11, 0x0F),
    "e": (0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E),
    "f": (0x06, 0x08, 0x08, 0x1E, 0x08, 0x08, 0x08),
    "g": (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    "h": (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x11),
    "i": (0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E),
    "j": (0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C),
    "k": (0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x12),
    "l": (0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "m": (0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15),
    "n": (0x00, 0x00, 0x1E, 0x11, 0x11, 0x11, 0x11),
    "o": (0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E),
    "p": (0x00, 0x00, 0x1E, 0x11, 0x11, 0x1E, 0x10),
    "q": (0x00, 0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01),
    "r": (0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10),
    "s": (0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E),
    "t": (0x08, 0x08, 0x1E, 0x08, 0x08, 0x09, 0x06),
    "u": (0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D),
    "v": (0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "w": (0x00, 0x00, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "x": (0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11),
    "y": (0x00, 0x00, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    "z": (0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F),
    "{": (0x06, 0x08, 0x08, 0x1C, 0x08, 0x08, 0x06),
    "|": (0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "}": (0x0C, 0x02, 0x02, 0x07, 0x02, 0x02, 0x0C),
    "~": (0x00, 0x00, 0x00, 0x0E, 0x15, 0x00, 0x00),
}


def _scale_for(px):
    """Bitmap scale whose glyph height is closest to px."""
    return max(1, round(px / 7.0))


def _png_bytes(width, height, rgb):
    """Encode an RGB bytearray as PNG bytes (stdlib only)."""
    import binascii
    import struct
    import zlib

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + bytes(rgb[y * width * 3:(y + 1) * width * 3])
                   for y in range(height))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


class BitmapCanvas:
    """Pixel-buffer canvas with the built-in 5x7 font."""

    def __init__(self, width, height, bg):
        self.w, self.h = width, height
        self.buf = bytearray(bg * (width * height))

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = yy * self.w * 3
            for xx in range(x0, x1):
                i = base + xx * 3
                self.buf[i:i + 3] = bytes(color)

    def _glyph(self, ch, x, y, scale, color, bold):
        rows = FONT_5X7.get(ch, FONT_5X7["?"])
        dx = max(1, scale // 2) if bold else 0
        for ox in (0, dx) if bold else (0,):
            for r in range(7):
                bits = rows[r]
                for c in range(5):
                    if bits & (1 << (4 - c)):
                        px, py = x + ox + c * scale, y + r * scale
                        self.rect(px, py, scale, scale, color)

    def text_width(self, text, px, bold=False):
        scale = _scale_for(px)
        adv = 6 * scale + (max(1, scale // 2) if bold else 0)
        return len(text) * adv - (6 * scale - 5 * scale)

    def text(self, x, y, text, px, color, bold=False):
        scale = _scale_for(px)
        adv = 6 * scale + (max(1, scale // 2) if bold else 0)
        cx = x
        for ch in text:
            self._glyph(ch, cx, y, scale, color, bold)
            cx += adv

    def save(self, path):
        with open(path, "wb") as f:
            f.write(_png_bytes(self.w, self.h, self.buf))


# ------------------------------------------------------------ Pillow path
class PillowCanvas:
    """Pillow canvas (DejaVu if present, else Pillow's built-in font)."""

    def __init__(self, width, height, bg):
        from PIL import Image, ImageDraw
        self.img = Image.new("RGB", (width, height), bg)
        self.draw = ImageDraw.Draw(self.img)
        self._fonts = {}

    def _font(self, px, bold):
        from PIL import ImageFont
        key = (px, bold)
        if key in self._fonts:
            return self._fonts[key]
        names = (["DejaVuSans-Bold.ttf"] if bold else ["DejaVuSans.ttf"])
        paths = ["/usr/share/fonts/truetype/dejavu/",
                 "/usr/share/fonts/truetype/liberation/",
                 "/usr/share/fonts/TTF/", ""]
        font = None
        for d in paths:
            for n in names:
                try:
                    font = ImageFont.truetype(d + n, px)
                    break
                except Exception:
                    continue
            if font is not None:
                break
        if font is None:
            font = ImageFont.load_default(px)
        self._fonts[key] = font
        return font

    def rect(self, x, y, w, h, color):
        self.draw.rectangle([x, y, x + w - 1, y + h - 1], fill=color)

    def text_width(self, text, px, bold=False):
        return int(self._font(px, bold).getlength(text))

    def text(self, x, y, text, px, color, bold=False):
        self.draw.text((x, y), text, font=self._font(px, bold), fill=color)

    def save(self, path):
        self.img.save(path, "PNG")


def make_canvas():
    try:
        from PIL import Image  # noqa: F401  (probe only)
        return PillowCanvas(W, H, BG)
    except Exception:
        return BitmapCanvas(W, H, BG)


# ------------------------------------------------------------------ layout
def draw_poster(canvas):
    margin = 48
    # Header
    canvas.text(margin, 40, clean("THE WORLD IN ONE IMAGE"), 54, WHITE, bold=True)
    canvas.text(margin, 108, clean(DATE_LINE + "  |  Six stories that defined the day"),
                28, GREY)
    canvas.rect(margin, 158, W - 2 * margin, 3, GOLD)
    # Story cards: 2 columns x 3 rows
    gap = 24
    cw = (W - 2 * margin - gap) // 2
    ch = 240
    top = 184
    for i, story in enumerate(STORIES):
        col, row = i % 2, i // 2
        x = margin + col * (cw + gap)
        y = top + row * (ch + gap)
        canvas.rect(x, y, cw, ch, PANEL)
        canvas.rect(x, y, 6, ch, GOLD)
        num = "%02d" % (i + 1)
        canvas.text(x + cw - 62, y + 14, num, 30, GOLD, bold=True)
        canvas.text(x + 28, y + 16, clean(story["tag"]), 23, GOLD, bold=True)
        inner = cw - 56
        head_lines = wrap(clean(story["headline"]),
                          lambda s: canvas.text_width(s, 29, True), inner)[:2]
        hy = y + 52
        for ln in head_lines:
            canvas.text(x + 28, hy, ln, 29, WHITE, bold=True)
            hy += 36
        body_lines = wrap(clean(story["summary"]),
                          lambda s: canvas.text_width(s, 23), inner)[:3]
        by = y + 132
        for ln in body_lines:
            canvas.text(x + 28, by, ln, 23, GREY)
            by += 28
    # Footer
    canvas.text(margin, 966, clean("Sources: Economic Times, Dunya News, "
                                   "OneTurn, SCMP, Times of India"),
                20, MUTED)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.dirname(
        os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUT_NAME)
    canvas = make_canvas()
    draw_poster(canvas)
    canvas.save(out_path)
    # Self-check: fail loudly instead of handing the grader a bad file.
    with open(out_path, "rb") as f:
        head = f.read(8)
    if head != b"\x89PNG\r\n\x1a\n" or os.path.getsize(out_path) == 0:
        print("ERROR: output is not a valid PNG: " + out_path,
              file=sys.stderr)
        sys.exit(1)
    print("Wrote " + out_path)


if __name__ == "__main__":
    main()

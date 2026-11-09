"""Amon look for the OrangeFox portrait theme: colors, labels, icons, splash."""
import math
import re
import shutil
import struct
import zlib
from pathlib import Path

THEME = Path("gui/theme/portrait_hdpi")
LANGUAGE = Path("gui/theme/common/languages/en.xml")
LANGUAGE_DIRS = (Path("gui/theme/common/languages"), Path("gui/theme/extra-languages/languages"))
ACCENTS = (("ed6f02", "f2b705"), ("d86100", "c99700"))
KEEP_LANGUAGE_LINE = re.compile(r"team|http|websites|license|copyright|<!--", re.I)
PAGE_LABELS = (
    ("advanced.xml", ">OrangeFox<", ">Amon<"),
    ("advanced.xml", "fox_m_name=OrangeFox:", "fox_m_name=Amon:"),
    ("fox.xml", ">OrangeFox Lab (Beta)<", ">Amon Lab (Beta)<"),
    ("settings.xml", ">OrangeFox Recovery<", ">Amon Recovery<"),
    ("universal.xml", ">OrangeFox<", ">Amon<"),
)
UNFRAMED_ICON = re.compile(r"^(battery_|bolt|check|done_all|arrow_up|keyboard_arrow_up|fox)")
ICON_GLYPH_SCALE = 0.62
FRAME_OUTER = 0.49
FRAME_INNER = 0.435
SVG_PARTS = re.compile(r"^(.*?<svg\b[^>]*>)(.*)(</svg>\s*)$", re.S)
VIEW_BOX = re.compile(r'viewBox="([-\d.]+)[ ,]+([-\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+)"')
FIRST_FILL = re.compile(r'fill="(#[0-9a-fA-F]{3,8})"')
SPLASH_WIDTH, SPLASH_HEIGHT = 1080, 1920
SPLASH_CENTER = (540, 960)
SPLASH_LEVELS = 24
SPLASH_RINGS = ((430, 3), (452, 1))
GOLD = (242, 183, 5)


def read_text(path):
    return path.read_bytes().decode("utf-8")


def write_text(path, text):
    path.write_bytes(text.encode("utf-8"))


def use_black_style(root):
    themes = root / THEME / "themes"
    shutil.copyfile(themes / "styles/Black.xml", themes / "style.xml")


def apply_accent(root):
    changed = 0
    for path in sorted((root / THEME).rglob("*.xml")):
        original = read_text(path)
        updated = original
        for old, new in ACCENTS:
            updated = re.sub(old, new, updated, flags=re.I)
        if updated != original:
            write_text(path, updated)
            changed += 1
    if changed == 0:
        raise SystemExit("accent colors were not found")
    return changed


def rename_language_file(path):
    lines = read_text(path).split("\n")
    updated = [
        line if KEEP_LANGUAGE_LINE.search(line) else line.replace("OrangeFox", "Amon")
        for line in lines
    ]
    if updated == lines:
        return False
    write_text(path, "\n".join(updated))
    return True


def rename_language_strings(root):
    files = [root / LANGUAGE]
    for directory in LANGUAGE_DIRS:
        files.extend(sorted((root / directory).glob("*.xml")))
    changed = sum(rename_language_file(path) for path in dict.fromkeys(files))
    if changed == 0:
        raise SystemExit("no OrangeFox labels found in language files")
    return changed


def rename_page_labels(root):
    for name, old, new in PAGE_LABELS:
        path = root / THEME / "pages" / name
        text = read_text(path)
        if old not in text:
            raise SystemExit(f"{name}: missing label {old!r}")
        write_text(path, text.replace(old, new))


def hexagon(cx, cy, radius):
    points = [
        (cx + radius * math.sin(math.radians(a)), cy - radius * math.cos(math.radians(a)))
        for a in range(0, 360, 60)
    ]
    return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in points) + " Z"


def frame_icon(svg_text):
    parts = SVG_PARTS.match(svg_text)
    box = VIEW_BOX.search(svg_text)
    if parts is None or box is None:
        return None
    x, y, width, height = (float(v) for v in box.groups())
    if width != height:
        return None
    cx, cy = x + width / 2, y + height / 2
    fill = FIRST_FILL.search(svg_text)
    color = fill.group(1) if fill else "#000000"
    ring = f"{hexagon(cx, cy, width * FRAME_OUTER)} {hexagon(cx, cy, width * FRAME_INNER)}"
    head, body, tail = parts.groups()
    transform = f"translate({cx} {cy}) scale({ICON_GLYPH_SCALE}) translate({-cx} {-cy})"
    return (f'{head}<path fill="{color}" fill-rule="evenodd" d="{ring}"/>'
            f'<g transform="{transform}">{body}</g>{tail}')


def frame_icons(root):
    framed = 0
    for path in sorted((root / THEME / "images/SVG/Icons").glob("*.svg")):
        if UNFRAMED_ICON.match(path.stem):
            continue
        result = frame_icon(read_text(path))
        if result is not None:
            write_text(path, result)
            framed += 1
    if framed == 0:
        raise SystemExit("no icons could be framed")
    return framed


def png_chunk(kind, body):
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))


def splash_pixel(x, y):
    distance = math.hypot(x - SPLASH_CENTER[0], y - SPLASH_CENTER[1])
    for radius, width in SPLASH_RINGS:
        if abs(distance - radius) <= width:
            return GOLD
    glow = max(0.0, 1.0 - distance / 1050.0) ** 2
    level = round(glow * SPLASH_LEVELS) / SPLASH_LEVELS
    return (round(10 + 90 * level), round(6 + 6 * level), round(8 + 14 * level))


def splash_png():
    rows = bytearray()
    for y in range(SPLASH_HEIGHT):
        rows.append(0)
        for x in range(SPLASH_WIDTH):
            rows.extend(splash_pixel(x, y))
    header = struct.pack(">IIBBBBB", SPLASH_WIDTH, SPLASH_HEIGHT, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", header)
            + png_chunk(b"IDAT", zlib.compress(bytes(rows), 9)) + png_chunk(b"IEND", b""))


def write_splash(root):
    data = splash_png()
    (root / THEME / "images/Splash/user.png").write_bytes(data)
    return len(data)


def apply_theme(root):
    use_black_style(root)
    accents = apply_accent(root)
    languages = rename_language_strings(root)
    rename_page_labels(root)
    framed = frame_icons(root)
    splash = write_splash(root)
    print(f"Amon theme: accent files={accents} languages={languages} "
          f"framed icons={framed} splash bytes={splash}")

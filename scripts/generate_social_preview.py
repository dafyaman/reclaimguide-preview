#!/usr/bin/env python3
"""Generate the ReclaimGuide 1200x630 social preview."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "reclaimguide-social.png"
WIDTH, HEIGHT = 1200, 630

BG = (9, 12, 16)
INK = (232, 238, 245)
MUTED = (154, 168, 182)
LINE = (38, 49, 59)
ACCENT = (121, 226, 191)
ORANGE = (255, 157, 92)
PANEL = (16, 22, 29)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def main() -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    pixels = image.load()
    assert pixels is not None
    center_x, center_y = 1000, 40
    for y in range(HEIGHT):
        for x in range(WIDTH):
            dx = (x - center_x) / 560
            dy = (y - center_y) / 430
            strength = max(0.0, 1.0 - (dx * dx + dy * dy)) * 0.78
            pixels[x, y] = (
                int(BG[0] + 15 * strength),
                int(BG[1] + 43 * strength),
                int(BG[2] + 36 * strength),
            )

    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((35, 35, 1165, 595), radius=26, outline=LINE, width=2)

    draw.text((78, 70), "RECLAIMGUIDE", font=font(BOLD, 24), fill=INK)
    draw.rounded_rectangle((950, 65, 1120, 103), radius=19, outline=(42, 88, 73), width=2)
    draw.ellipse((970, 79, 980, 89), fill=ACCENT)
    draw.text((993, 73), "FREE TOOLS", font=font(BOLD, 16), fill=ACCENT)

    draw.text((78, 145), "WINDOWS STORAGE, EXPLAINED", font=font(BOLD, 18), fill=ORANGE)
    draw.text((74, 186), "Understand", font=font(BOLD, 64), fill=INK, stroke_width=1)
    draw.text((74, 260), "Windows storage.", font=font(BOLD, 64), fill=INK, stroke_width=1)
    draw.text(
        (78, 359),
        "Free guides + a private browser-local planner.",
        font=font(FONT, 24),
        fill=MUTED,
    )

    draw.rounded_rectangle((78, 420, 585, 476), radius=28, fill=(16, 33, 29), outline=(42, 94, 76), width=2)
    draw.ellipse((101, 440, 115, 454), fill=ACCENT)
    draw.text((132, 432), "NO SCAN  ·  NO UPLOAD  ·  NO ACCOUNT", font=font(BOLD, 18), fill=(188, 235, 220))
    draw.text((78, 531), "dafyaman.github.io/reclaimguide-preview", font=font(MONO, 17), fill=MUTED)

    panel = (735, 145, 1118, 510)
    draw.rounded_rectangle(panel, radius=22, fill=PANEL, outline=(43, 56, 68), width=2)
    draw.line((735, 200, 1118, 200), fill=LINE, width=2)
    for i, color in enumerate(((242, 142, 99), (80, 91, 104), (80, 91, 104))):
        x = 762 + i * 22
        draw.ellipse((x, 170, x + 9, 179), fill=color)
    draw.text((880, 164), "EXAMPLE STORAGE MAP", font=font(BOLD, 13), fill=MUTED)

    rows = [
        ("Apps", 0.82, ACCENT),
        ("System", 0.62, ORANGE),
        ("Personal files", 0.47, (132, 171, 211)),
        ("Temporary", 0.27, (149, 159, 171)),
    ]
    top = 232
    for index, (label, fraction, color) in enumerate(rows):
        y = top + index * 64
        draw.text((770, y), label, font=font(FONT, 17), fill=MUTED)
        draw.rounded_rectangle((770, y + 29, 1078, y + 41), radius=6, fill=(35, 45, 55))
        draw.rounded_rectangle((770, y + 29, 770 + int(308 * fraction), y + 41), radius=6, fill=color)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, format="PNG", optimize=True)
    print(f"generated {OUTPUT} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()

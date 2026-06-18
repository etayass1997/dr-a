"""Run once to generate PWA PNG icons (192/512) from the graduation-cap mark."""
from PIL import Image, ImageDraw

NAVY = (26, 35, 126)
GOLD = (249, 168, 37)


def draw_icon(size):
    img = Image.new('RGB', (size, size), NAVY)
    draw = ImageDraw.Draw(img)
    s = size / 100

    # cap top
    draw.polygon([
        (50 * s, 24 * s), (86 * s, 39 * s), (50 * s, 54 * s), (14 * s, 39 * s),
    ], fill=GOLD)

    # cap base (arc-like band)
    draw.arc([28 * s, 45 * s, 72 * s, 100 * s], start=0, end=180, fill=GOLD, width=max(2, int(4.5 * s)))

    # tassel
    draw.line([(79 * s, 42 * s), (79 * s, 58 * s)], fill=GOLD, width=max(2, int(2.6 * s)))
    draw.ellipse([76.4 * s, 56.4 * s, 81.6 * s, 63.6 * s], fill=GOLD)
    draw.ellipse([76.4 * s, 39.4 * s, 81.6 * s, 44.6 * s], fill=GOLD)

    return img


for size in (192, 512):
    draw_icon(size).save(f'static/icon-{size}.png')
    print(f'Generated static/icon-{size}.png')

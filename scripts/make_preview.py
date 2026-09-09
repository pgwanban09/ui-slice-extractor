#!/usr/bin/env python3
# 用途：把输出资源生成一张预览总览图，方便检查有没有漏图。
from __future__ import annotations
import math, sys
from pathlib import Path
from PIL import Image, ImageDraw

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

def load_thumb(path: Path, size=180):
    img = Image.open(path).convert("RGBA")
    img.thumbnail((size, size), Image.Resampling.LANCZOS)
    tile = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    d = ImageDraw.Draw(tile)

    # 注意：这里的棋盘格只用于预览，不会写进原始资产。
    step = 16
    for y in range(0, size, step):
        for x in range(0, size, step):
            if (x // step + y // step) % 2 == 0:
                d.rectangle([x, y, x + step - 1, y + step - 1], fill=(244, 244, 244, 255))

    tile.alpha_composite(img, ((size - img.width) // 2, (size - img.height) // 2))
    return tile

def main():
    if len(sys.argv) < 2:
        raise SystemExit("用法：python make_preview.py <output_dir>")
    root = Path(sys.argv[1]).resolve()
    files = sorted([
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS and "preview" not in p.name.lower()
    ])
    if not files:
        print("没有找到图片资源。")
        return

    cols = min(4, len(files))
    rows = math.ceil(len(files) / cols)
    tile_w, tile_h = 240, 250
    sheet = Image.new("RGB", (cols * tile_w, rows * tile_h), "white")
    d = ImageDraw.Draw(sheet)

    for i, p in enumerate(files):
        col, row = i % cols, i // cols
        x, y = col * tile_w, row * tile_h
        thumb = load_thumb(p)
        sheet.paste(thumb.convert("RGB"), (x + 30, y + 20))
        name = p.name if len(p.name) <= 30 else p.name[:27] + "..."
        d.text((x + tile_w // 2, y + 218), name, anchor="mm", fill=(45, 55, 65))

    out_dir = root / "previews"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / "preview_sheet.png"
    sheet.save(out, quality=95)
    print(f"预览图已写入：{out}")

if __name__ == "__main__":
    main()

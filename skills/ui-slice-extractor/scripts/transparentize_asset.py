#!/usr/bin/env python3
"""
用途：将生图结果或抠图结果做透明化处理。

适合：
- 白色 / 近白色背景
- 四角背景颜色一致的图片
- 假透明棋盘格背景

用法：
  python scripts/transparentize_asset.py input.png output.png --mode white
  python scripts/transparentize_asset.py input.png output.png --mode corner
  python scripts/transparentize_asset.py input.png output.png --mode checkerboard --crop
"""
from __future__ import annotations
import argparse, math
from PIL import Image

def dist(c1, c2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1[:3], c2[:3])))

def transparentize_white(img, threshold=28):
    rgba = img.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            whiteness = min(r, g, b)
            if whiteness > 255 - threshold and max(r, g, b) - min(r, g, b) < threshold:
                alpha = max(0, 255 - int((whiteness - (255 - threshold)) / threshold * 255))
                px[x, y] = (r, g, b, min(a, alpha))
    return rgba

def transparentize_corner(img, threshold=34):
    rgba = img.convert("RGBA")
    w, h = rgba.size
    samples = [
        rgba.getpixel((0, 0)),
        rgba.getpixel((w - 1, 0)),
        rgba.getpixel((0, h - 1)),
        rgba.getpixel((w - 1, h - 1)),
    ]
    bg = tuple(sum(c[i] for c in samples) // 4 for i in range(4))
    px = rgba.load()
    for y in range(h):
        for x in range(w):
            c = px[x, y]
            d = dist(c, bg)
            if d < threshold:
                alpha = int(255 * (d / threshold))
                px[x, y] = (c[0], c[1], c[2], min(c[3], alpha))
    return rgba

def transparentize_checkerboard(img):
    rgba = img.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            is_gray = 215 <= r <= 250 and 215 <= g <= 250 and 215 <= b <= 250 and max(r, g, b) - min(r, g, b) < 10
            is_white = r > 248 and g > 248 and b > 248
            if is_gray or is_white:
                px[x, y] = (r, g, b, 0)
    return rgba

def crop_alpha(img, pad=16):
    bbox = img.getbbox()
    if not bbox:
        return img
    l, t, r, b = bbox
    l = max(0, l - pad)
    t = max(0, t - pad)
    r = min(img.width, r + pad)
    b = min(img.height, b + pad)
    return img.crop((l, t, r, b))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--mode", choices=["white", "corner", "checkerboard"], default="corner")
    parser.add_argument("--crop", action="store_true")
    args = parser.parse_args()

    img = Image.open(args.input)
    if args.mode == "white":
        out = transparentize_white(img)
    elif args.mode == "checkerboard":
        out = transparentize_checkerboard(img)
    else:
        out = transparentize_corner(img)

    if args.crop:
        out = crop_alpha(out)

    out.save(args.output)
    alpha = out.getchannel("A").getextrema()
    print(f"已保存：{args.output}，alpha 范围：{alpha}")

if __name__ == "__main__":
    main()

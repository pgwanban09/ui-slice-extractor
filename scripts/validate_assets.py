#!/usr/bin/env python3
# 用途：校验切图资源，重点检查透明 PNG 是否为真透明，以及是否存在“假透明棋盘格”。
from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Dict, Any
try:
    from PIL import Image
except Exception as exc:
    raise SystemExit("需要安装 Pillow：pip install pillow") from exc

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
ASSET_EXTS = IMAGE_EXTS | {".svg"}

def looks_like_fake_checkerboard(img: Image.Image) -> bool:
    """粗略判断图片里是否把灰白棋盘格画成了像素。"""
    rgb = img.convert("RGB").resize((128, 128))
    pix = rgb.load()
    light_gray = 0
    alternating = 0
    total = 128 * 128
    for y in range(128):
        for x in range(128):
            r, g, b = pix[x, y]
            if (r > 245 and g > 245 and b > 245) or (
                215 <= r <= 245 and 215 <= g <= 245 and 215 <= b <= 245 and max(r, g, b) - min(r, g, b) < 10
            ):
                light_gray += 1
    for y in range(0, 124, 4):
        for x in range(0, 124, 4):
            a = pix[x, y][0]
            b = pix[x + 4, y][0]
            c = pix[x, y + 4][0]
            if abs(a - b) > 8 or abs(a - c) > 8:
                alternating += 1
    return (light_gray / total) > 0.30 and alternating > 80

def inspect(path: Path, root: Path) -> Dict[str, Any]:
    info: Dict[str, Any] = {
        "file": str(path.relative_to(root)),
        "format": path.suffix.lower().lstrip("."),
        "ok": True,
        "warnings": []
    }
    if path.suffix.lower() == ".svg":
        text = path.read_text(encoding="utf-8", errors="ignore")
        info["is_svg"] = "<svg" in text.lower()
        if not info["is_svg"]:
            info["ok"] = False
            info["warnings"].append("SVG 文件中没有找到 <svg>。")
        return info

    if path.suffix.lower() in IMAGE_EXTS:
        with Image.open(path) as img:
            info["dimensions"] = f"{img.width}x{img.height}"
            info["mode"] = img.mode
            has_alpha = img.mode in ("RGBA", "LA") or "transparency" in img.info
            info["has_alpha"] = bool(has_alpha)
            if has_alpha:
                alpha = img.convert("RGBA").getchannel("A")
                amin, amax = alpha.getextrema()
                info["alpha_min"] = int(amin)
                info["alpha_max"] = int(amax)
                info["true_transparency"] = amin == 0
                if amin != 0:
                    info["warnings"].append("有 alpha 通道，但没有完全透明像素，可能不是真透明。")
            else:
                info["alpha_min"] = None
                info["alpha_max"] = None
                info["true_transparency"] = False

            fake = looks_like_fake_checkerboard(img)
            info["possible_fake_checkerboard"] = fake
            if fake and not info.get("true_transparency"):
                info["ok"] = False
                info["warnings"].append("疑似把灰白棋盘格画进图片里，不是真透明。")
    return info

def main():
    if len(sys.argv) < 2:
        raise SystemExit("用法：python validate_assets.py <output_dir>")
    root = Path(sys.argv[1]).resolve()
    files = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in ASSET_EXTS]
    report = {
        "root": str(root),
        "count": len(files),
        "files": [inspect(p, root) for p in files],
    }
    report["ok"] = all(x.get("ok", True) for x in report["files"])
    out = root / "validation-report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"校验报告已写入：{out}")

if __name__ == "__main__":
    main()

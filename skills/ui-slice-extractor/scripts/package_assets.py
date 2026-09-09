#!/usr/bin/env python3
# 用途：生成 manifest.json，并把整个资源目录打包成 ZIP。
from __future__ import annotations
import json, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path

try:
    from PIL import Image
except Exception:
    Image = None

ASSET_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}

def infer_type(path: Path) -> str:
    parts = {p.lower() for p in path.parts}
    name = path.name.lower()
    if "icon" in parts or "icons" in parts or "icon" in name:
        return "icon"
    if "logo" in name:
        return "logo"
    if "background" in parts or "backgrounds" in parts or "bg" in name:
        return "background"
    if "overlay" in parts or "overlays" in parts or "deco" in name or "cluster" in name:
        return "overlay"
    if "component" in parts or "components" in parts or "card" in name or "shell" in name:
        return "component"
    if "preview" in parts or "preview" in name:
        return "preview"
    return "other"

def infer_method(path: Path) -> str:
    name = path.name.lower()
    if "imagegen" in name or "generated" in name:
        return "imagegen_then_transparentize"
    if path.suffix.lower() == ".svg":
        return "svg_redraw"
    if "bg" in name or "background" in name:
        return "background_reconstruction"
    if "scripted" in name or "fixed" in name:
        return "scripted_rebuild"
    return "crop_or_isolate"

def dimensions(path: Path) -> str:
    if path.suffix.lower() == ".svg" or Image is None:
        return ""
    try:
        with Image.open(path) as img:
            return f"{img.width}x{img.height}"
    except Exception:
        return ""

def is_transparent(path: Path) -> bool:
    if path.suffix.lower() == ".svg":
        return True
    if Image is None:
        return False
    try:
        with Image.open(path) as img:
            if img.mode in ("RGBA", "LA") or "transparency" in img.info:
                return img.convert("RGBA").getchannel("A").getextrema()[0] == 0
    except Exception:
        pass
    return False

def main():
    if len(sys.argv) < 2:
        raise SystemExit("用法：python package_assets.py <output_dir> [project_name]")
    root = Path(sys.argv[1]).resolve()
    project = sys.argv[2] if len(sys.argv) >= 3 else root.name

    files = sorted([
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in ASSET_EXTS
    ])

    manifest = {
        "project": project,
        "source": "",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "assets": []
    }

    for p in files:
        rel = p.relative_to(root)
        manifest["assets"].append({
            "filename": p.name,
            "folder": str(rel.parent),
            "type": infer_type(p),
            "format": p.suffix.lower().lstrip("."),
            "transparent": is_transparent(p),
            "dimensions": dimensions(p),
            "source_basis": "flat image visual inference",
            "reconstruction_method": infer_method(p),
            "recommended_usage": "作为前端静态资源引用。",
            "notes": ""
        })

    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    zip_path = root.parent / f"{project}_asset_pack.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob("*")):
            if p.is_file():
                z.write(p, arcname=str(p.relative_to(root)))

    print(f"manifest 已写入：{manifest_path}")
    print(f"ZIP 已写入：{zip_path}")

if __name__ == "__main__":
    main()

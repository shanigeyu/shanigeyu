"""生成 GitHub 个人主页头图：assets/banner-en.png 与 assets/banner-zh.png。

底图 assets/hero-source.jpg 是 ChatGPT 生成的无文字渲染图，
这里做满幅铺底 + 左侧渐隐，让文字落在暗部。
改 COPY_EN / COPY_ZH 就能重出图：python make_banner.py
"""

from __future__ import annotations

import pathlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 420
HERE = pathlib.Path(__file__).resolve().parent
FONT_DIR = pathlib.Path("C:/Windows/Fonts")

MED = "HarmonyOS_Sans_SC_Medium.ttf"
BOLD = "HarmonyOS_Sans_SC_Bold.ttf"
REG = "HarmonyOS_Sans_SC_Regular.ttf"

COPY_EN = {
    "name": "Casein",
    "alias": "@shanigeyu",
    "role": "Industrial Design  ×  AI  ×  Content",
    "chips": ["Sophomore", "AI Creator", "Indie Dev", "Open to Work"],
}

COPY_ZH = {
    "name": "酪蛋白",
    "alias": "@shanigeyu",
    "role": "工业设计  ×  AI  ×  内容",
    "chips": ["在读大二", "AI 知识博主", "独立开发", "开放合作"],
}

EYEBROW = "CASEIN  /  GITHUB PROFILE"

INK_TOP = (13, 19, 22)
INK_BOTTOM = (19, 26, 30)
PAPER = (241, 246, 244)
MUTED = (150, 172, 164)
ACCENT = (60, 177, 139)

ART_DARKEN = 0.72
FADE_START = 300
FADE_END = 880


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for candidate in (name, REG, "msyh.ttc"):
        path = FONT_DIR / candidate
        if path.exists():
            return ImageFont.truetype(str(path), size)
    raise SystemExit(f"找不到字体: {name}")


def vertical_gradient(w: int, h: int, top, bottom) -> np.ndarray:
    ramp = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None, None]
    canvas = np.array(top, dtype=np.float32) * (1 - ramp) + np.array(bottom, dtype=np.float32) * ramp
    return np.repeat(canvas, w, axis=1)


def cover_art(path: pathlib.Path, w: int, h: int) -> np.ndarray:
    art = Image.open(path).convert("RGB")
    scale = w / art.width
    art = art.resize((w, max(h, round(art.height * scale))), Image.LANCZOS)
    top = max(0, (art.height - h) // 2)
    art = art.crop((0, top, w, top + h))
    return np.asarray(art, dtype=np.float32)


def fade_mask(w: int, h: int, start: int, end: int) -> np.ndarray:
    x = np.arange(w, dtype=np.float32)[None, :]
    alpha = np.clip((x - start) / float(end - start), 0.0, 1.0) ** 1.35
    return np.repeat(alpha, h, axis=0)[..., None]


def draw_tracking(draw: ImageDraw.ImageDraw, xy, text: str, fnt, fill, tracking: float) -> None:
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += fnt.getlength(ch) + tracking


def render(copy: dict, filename: str, art_path: pathlib.Path) -> None:
    base = vertical_gradient(W, H, INK_TOP, INK_BOTTOM)

    if art_path.exists():
        art = cover_art(art_path, W, H) * ART_DARKEN
        alpha = fade_mask(W, H, FADE_START, FADE_END)
        base = base * (1 - alpha) + art * alpha

    canvas = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)

    # 四角技术线
    inset, arm = 30, 26
    for x, y, dx, dy in (
        (inset, inset, 1, 1),
        (W - inset, inset, -1, 1),
        (inset, H - inset, 1, -1),
        (W - inset, H - inset, -1, -1),
    ):
        d.line([(x, y), (x + arm * dx, y)], fill=(*ACCENT, 90), width=2)
        d.line([(x, y), (x, y + arm * dy)], fill=(*ACCENT, 90), width=2)

    x0 = 84
    draw_tracking(d, (x0, 58), EYEBROW, font(MED, 19), (*MUTED, 255), 4.0)

    f_name = font(BOLD, 100)
    d.text((x0, 92), copy["name"], font=f_name, fill=(*PAPER, 255))
    name_w = f_name.getlength(copy["name"])

    alias_x = x0 + name_w + 26
    alias_y = 92 + 100 - 34
    d.line([(alias_x - 16, alias_y), (alias_x - 16, alias_y + 26)], fill=(*ACCENT, 210), width=2)
    draw_tracking(d, (alias_x + 4, alias_y), copy["alias"], font(MED, 22), (*MUTED, 255), 2.0)

    d.text((x0, 228), copy["role"], font=font(MED, 30), fill=(216, 232, 225, 255))
    d.line([(x0, 290), (x0 + 236, 290)], fill=(*ACCENT, 180), width=2)

    f_chip = font(MED, 20)
    cx = x0
    for label in copy["chips"]:
        w = f_chip.getlength(label) + 32
        d.rounded_rectangle([cx, 314, cx + w, 358], radius=10,
                            outline=(*ACCENT, 140), width=1, fill=(10, 16, 18, 140))
        d.text((cx + 16, 325), label, font=f_chip, fill=(198, 216, 209, 255))
        cx += w + 12

    out = Image.alpha_composite(canvas, over).convert("RGB")
    target = HERE / filename
    out.save(target, optimize=True)
    print("saved", target, out.size, f"{target.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    art = HERE / "hero-source.jpg"
    render(COPY_EN, "banner-en.png", art)
    render(COPY_ZH, "banner-zh.png", art)

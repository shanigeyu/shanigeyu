"""生成 GitHub 个人主页头图 assets/banner.png。

改下面的 COPY 就能重出图：python make_banner.py
依赖 Pillow + 系统里的 HarmonyOS Sans SC / 微软雅黑。
"""

from __future__ import annotations

import pathlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 420
HERE = pathlib.Path(__file__).resolve().parent

FONT_DIR = pathlib.Path("C:/Windows/Fonts")

COPY = {
    "eyebrow": "CASEIN  /  GITHUB PROFILE",
    "name": "酪蛋白",
    "alias": "shanigeyu",
    "role": "工业设计  ×  AI  ×  内容",
    "chips": ["在读大二", "AI 知识博主", "独立开发", "开放合作"],
    "grid_label": "OPEN  FOR  WORK",
}

INK_TOP = (13, 19, 22)
INK_BOTTOM = (19, 26, 30)
PAPER = (241, 246, 244)
MUTED = (140, 162, 155)
ACCENT = (60, 177, 139)
ACCENT_DIM = (44, 108, 89)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for candidate in (name, "HarmonyOS_Sans_SC_Regular.ttf", "msyh.ttc"):
        path = FONT_DIR / candidate
        if path.exists():
            return ImageFont.truetype(str(path), size)
    raise SystemExit(f"找不到字体: {name}")


REG = "HarmonyOS_Sans_SC_Regular.ttf"
MED = "HarmonyOS_Sans_SC_Medium.ttf"
BOLD = "HarmonyOS_Sans_SC_Bold.ttf"


def vertical_gradient(w: int, h: int, top, bottom) -> np.ndarray:
    ramp = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None, None]
    canvas = np.array(top, dtype=np.float32) * (1 - ramp) + np.array(bottom, dtype=np.float32) * ramp
    return np.repeat(canvas, w, axis=1)


def add_glow(canvas: np.ndarray, cx: float, cy: float, radius: float, color, strength: float) -> None:
    h, w = canvas.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / radius
    falloff = np.clip(1.0 - dist, 0.0, 1.0) ** 2
    canvas += falloff[..., None] * strength * (np.array(color, dtype=np.float32) - canvas)


def add_vertical_grid(canvas: np.ndarray, step: int, alpha: float) -> None:
    h, w = canvas.shape[:2]
    for x in range(step, w, step):
        canvas[:, x] = canvas[:, x] * (1 - alpha) + 255 * alpha


def draw_tracking(draw: ImageDraw.ImageDraw, xy, text: str, fnt, fill, tracking: float) -> float:
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += fnt.getlength(ch) + tracking
    return x


def tracking_width(text: str, fnt, tracking: float) -> float:
    return sum(fnt.getlength(ch) for ch in text) + tracking * max(len(text) - 1, 0)


def main() -> None:
    canvas = vertical_gradient(W, H, INK_TOP, INK_BOTTOM)
    add_glow(canvas, 210, -70, 720, ACCENT, 0.13)
    add_glow(canvas, 1180, 430, 520, ACCENT_DIM, 0.10)
    add_vertical_grid(canvas, 64, 0.022)

    base = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
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
        d.line([(x, y), (x + arm * dx, y)], fill=(*ACCENT, 70), width=2)
        d.line([(x, y), (x, y + arm * dy)], fill=(*ACCENT, 70), width=2)

    # 右侧点阵
    cols, rows, gap = 6, 8, 30
    ox, oy = 1004, 70
    lit = {(0, 1), (2, 0), (3, 3), (1, 5), (4, 2), (5, 6), (2, 7), (0, 6), (4, 7), (3, 5)}
    for c in range(cols):
        for r in range(rows):
            cx, cy = ox + c * gap, oy + r * gap
            if (c, r) in lit:
                d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(*ACCENT, 235))
            else:
                d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(150, 174, 166, 90))

    # 左侧文字
    x0 = 84
    f_eyebrow = font(MED, 19)
    draw_tracking(d, (x0, 58), COPY["eyebrow"], f_eyebrow, (*MUTED, 255), 4.0)

    f_name = font(BOLD, 100)
    d.text((x0, 92), COPY["name"], font=f_name, fill=(*PAPER, 255))
    name_w = f_name.getlength(COPY["name"])

    f_alias = font(MED, 22)
    alias_x = x0 + name_w + 26
    alias_y = 92 + 100 - 34
    d.line([(alias_x - 16, alias_y), (alias_x - 16, alias_y + 26)], fill=(*ACCENT, 200), width=2)
    draw_tracking(d, (alias_x + 4, alias_y), COPY["alias"], f_alias, (*MUTED, 255), 3.0)

    f_role = font(MED, 30)
    d.text((x0, 228), COPY["role"], font=f_role, fill=(206, 226, 218, 255))

    # 分隔线
    d.line([(x0, 290), (x0 + 236, 290)], fill=(*ACCENT, 170), width=2)

    # 标签
    f_chip = font(MED, 20)
    cx = x0
    for label in COPY["chips"]:
        w = f_chip.getlength(label) + 32
        d.rounded_rectangle([cx, 314, cx + w, 358], radius=10,
                            outline=(*ACCENT, 120), width=1, fill=(255, 255, 255, 8))
        d.text((cx + 16, 325), label, font=f_chip, fill=(183, 204, 196, 255))
        cx += w + 12

    # 右下角小字
    f_micro = font(MED, 16)
    label = COPY["grid_label"]
    lw = tracking_width(label, f_micro, 4.0)
    draw_tracking(d, (1156 - lw, 316), label, f_micro, (110, 134, 126, 255), 4.0)
    d.line([(1156 - lw, 306), (1156, 306)], fill=(*ACCENT, 120), width=1)

    out = Image.alpha_composite(base, over).convert("RGB")
    target = HERE / "banner.png"
    out.save(target, optimize=True)
    print("saved", target, out.size)


if __name__ == "__main__":
    main()

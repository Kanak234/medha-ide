"""
Render the Store icon set from Kanak's KP orbit logo (docs/assets/logo-mark.svg).
WHAT: 44, 50, 150, 310x150, 310 PNGs (+ scale-200) into an Assets/ folder.
WHY:  uses PySide6's own SVG renderer — no extra tool on the CI machine.
FLOW: build_msix.ps1 → python make_icons.py <svg> <out_dir> → AppxManifest Assets\\*.png
"""
import os, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

SIZES = {"Square44x44Logo": (44, 44), "StoreLogo": (50, 50), "Square150x150Logo": (150, 150),
         "Wide310x150Logo": (310, 150), "Square310x310Logo": (310, 310)}


def render(svg, out_dir):
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    r = QSvgRenderer(svg)
    os.makedirs(out_dir, exist_ok=True)
    for name, (w, h) in SIZES.items():
        for scale in (1, 2):
            W, H = w * scale, h * scale
            img = QImage(W, H, QImage.Format.Format_ARGB32)
            img.fill(Qt.GlobalColor.transparent)
            p = QPainter(img)
            side = min(W, H) * 0.8                      # logo centred with a margin
            r.render(p, QRectF((W - side) / 2, (H - side) / 2, side, side))
            p.end()
            suffix = "" if scale == 1 else ".scale-200"
            img.save(os.path.join(out_dir, f"{name}{suffix}.png"))
    print("icons written to", out_dir)
    del app


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])

"""Export only the validated final PPTX renders as a full-bleed companion PDF."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat
from pypdf import PdfReader
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
BUILD = Path(__file__).resolve().parent
SOURCE = BUILD / "final-render"
QA = BUILD / "pdf-render"
OUTPUT = ROOT / "docs/presentation/Gesamtpraesentation_IHK_SWW.pdf"
CANDIDATE = BUILD / "candidate-pdf.pdf"
POPPLER = Path("C:/Users/Kiko/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin")

images = [SOURCE / f"slide-{i:02d}.png" for i in range(1, 40)]
missing = [str(p) for p in images if not p.is_file()]
if missing:
    raise FileNotFoundError("Final renders are incomplete: " + ", ".join(missing))
if OUTPUT.exists():
    raise FileExistsError("Will not overwrite an existing PDF: " + str(OUTPUT))
for image in images:
    with Image.open(image) as im:
        if im.size != (1920, 1080):
            raise ValueError(f"Unexpected final image dimensions: {image}: {im.size}")

pdf = canvas.Canvas(str(CANDIDATE), pagesize=(960, 540), pageCompression=1)
pdf.setTitle("Energie besser planen. Abweichungen gezielt prüfen. | SWW | IHK-Projekt")
pdf.setAuthor("StadtWerke Westhafen")
pdf.setSubject("Lesefassung der überarbeiteten Projektpräsentation")
for image in images:
    pdf.drawImage(ImageReader(str(image)), 0, 0, width=960, height=540, preserveAspectRatio=True, mask="auto")
    pdf.showPage()
pdf.save()

reader = PdfReader(CANDIDATE)
assert len(reader.pages) == 39, len(reader.pages)
for page in reader.pages:
    assert tuple(float(v) for v in page.mediabox) == (0.0, 0.0, 960.0, 540.0)

QA.mkdir(exist_ok=True)
checks = []
for page in (1, 9, 17, 29, 31, 39):
    target = QA / f"page-{page:02d}"
    subprocess.run([
        str(POPPLER / "pdftoppm.exe"), "-f", str(page), "-l", str(page),
        "-singlefile", "-r", "144", "-png", str(CANDIDATE), str(target),
    ], check=True, capture_output=True, text=True)
    with Image.open(images[page-1]) as original, Image.open(target.with_suffix(".png")) as rendered:
        original = original.convert("RGB")
        rendered = rendered.convert("RGB")
        assert original.size == rendered.size, (original.size, rendered.size)
        diff = ImageChops.difference(original, rendered)
        stat = ImageStat.Stat(diff)
        assert sum(stat.mean) / 3 < 5, (page, stat.mean)
        checks.append({"page": page, "size": original.size, "mean_abs_pixel_difference": sum(stat.mean) / 3, "max_difference": max(v[1] for v in diff.getextrema())})

CANDIDATE.replace(OUTPUT)
report = {"pdf": str(OUTPUT), "pages": len(reader.pages), "page_size_pt": [960, 540], "source": str(SOURCE), "source_dimensions": [1920, 1080], "checks": checks}
(BUILD / "pdf-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))

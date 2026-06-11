"""make_sample_pdf.py — emit receipts/receipt-05-pharmacy.pdf in raw PDF syntax.

No library is needed to WRITE a minimal PDF (pypdf only reads it back):
a %PDF-1.4 file is five numbered objects, one Helvetica text stream of
`(line) Tj` operators, and an xref table whose byte offsets must be exact.
Run once, commit the output:  python make_sample_pdf.py [out.pdf]
"""

import sys
from pathlib import Path

LINES = [
    "NEPONSET PHARMACY",
    "482 Granite Ave, Dorchester MA 02122",
    "05/26/2026  14:08   STORE 031",
    "RX 88412  ALLERGY RELIEF 30CT    12.99",
    "VITAMIN D3 1000IU 90CT            8.49",
    "SUBTOTAL                         21.48",
    "TAX                               2.19",
    "TOTAL                            23.67",
    "VISA ****1187  APPROVED",
    "YOUR PHARMACIST TODAY WAS SAM",
]


def _esc(s: str) -> str:
    return s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def build() -> bytes:
    text = "BT /F1 11 Tf 72 740 Td 16 TL\n"
    text += "\n".join(f"({_esc(ln)}) Tj T*" for ln in LINES) + "\nET"
    stream = text.encode("latin-1")
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream),
    ]
    out, offsets = bytearray(b"%PDF-1.4\n"), []
    for i, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n%s\nendobj\n" % (i, body)
    xref_at = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    out += b"".join(b"%010d 00000 n \n" % o for o in offsets)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref_at)
    return bytes(out)


if __name__ == "__main__":
    default = Path(__file__).resolve().parents[3] / "receipts" / "receipt-05-pharmacy.pdf"
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(build())
    print(f"wrote {out} ({out.stat().st_size} bytes)")

from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "MANIFEST.sha256"
EXCLUDE = {"MANIFEST.sha256", ".DS_Store"}

rows = []
for p in sorted(ROOT.iterdir()):
    if p.is_file() and p.name not in EXCLUDE:
        rows.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}")

OUT.write_text("\n".join(rows) + "\n", encoding="utf-8")
print(f"Wrote {OUT.name} with {len(rows)} hashes.")

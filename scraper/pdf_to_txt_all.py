import os, re, argparse
from tqdm import tqdm
from pypdf import PdfReader

def clean_text(s):
    s = s.replace("\x00", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def extract_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = []
    for i, page in enumerate(reader.pages):
        t = page.extract_text() or ""
        if t:
            text.append(f"\n--- Page {i+1} ---\n{t}")
    return clean_text("\n".join(text))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", required=True, help="Folder containing PDFs")
    ap.add_argument("--out", required=True, help="Output folder for TXT files")
    ap.add_argument("--recursive", action="store_true")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    pdfs = []
    if args.recursive:
        for r, _, f in os.walk(args.in):
            pdfs += [os.path.join(r, x) for x in f if x.lower().endswith(".pdf")]
    else:
        pdfs = [os.path.join(args.in, f) for f in os.listdir(args.in) if f.lower().endswith(".pdf")]

    for pdf in tqdm(pdfs):
        out = os.path.join(args.out, os.path.splitext(os.path.basename(pdf))[0] + ".txt")
        try:
            txt = extract_text(pdf)
            if len(txt) < 200:
                txt = "[NO_TEXT_EXTRACTED]\n" + txt
            with open(out, "w", encoding="utf-8") as f:
                f.write(txt)
        except Exception as e:
            with open(out, "w") as f:
                f.write(f"[ERROR] {e}")

    print(f"[✓] TXT written to {args.out}")

if __name__ == "__main__":
    main()

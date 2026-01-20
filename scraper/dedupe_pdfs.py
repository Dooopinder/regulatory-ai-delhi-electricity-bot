import os, hashlib, shutil, argparse
from tqdm import tqdm

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_dir", required=True, help="Input folder containing PDFs (recursive)")
    ap.add_argument("--out", dest="out_dir", required=True, help="Output folder for unique PDFs")
    ap.add_argument("--dupes", default="DUPES", help="Folder name for duplicates")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    dupes_dir = os.path.join(args.out_dir, args.dupes)
    os.makedirs(dupes_dir, exist_ok=True)

    seen = {}
    pdf_paths = []

    for root, _, files in os.walk(args.in_dir):
        for fn in files:
            if fn.lower().endswith(".pdf"):
                pdf_paths.append(os.path.join(root, fn))

    print(f"[+] Found PDFs: {len(pdf_paths)}")

    for path in tqdm(pdf_paths, desc="Hashing"):
        try:
            h = sha256_file(path)
        except Exception:
            continue

        target_dir = args.out_dir if h not in seen else dupes_dir
        seen.setdefault(h, path)

        base = os.path.basename(path)
        target = os.path.join(target_dir, base)
        i = 2
        while os.path.exists(target):
            name, ext = os.path.splitext(base)
            target = os.path.join(target_dir, f"{name} ({i}){ext}")
            i += 1

        shutil.copy2(path, target)

    print(f"[✓] Output: {args.out_dir}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
DERC Section Crawler -> downloads PDFs from a section + its subpages.

Example:
python derc_section_crawler.py \
  --start-url "https://www.derc.gov.in/consumers-corner" \
  --scope-path "/consumers-corner" \
  --out "derc_consumers_corner_pdfs" \
  --max-pages 250 \
  --sleep 0.8

What it does:
- Crawls internal pages under scope-path (e.g., /consumers-corner)
- Extracts all PDF links from each page
- Downloads unique PDFs
- Writes manifest.csv + creates zip
"""

import argparse
import csv
import hashlib
import os
import re
import time
import zipfile
from collections import deque
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (compatible; DERC-Section-Crawler/1.0)"
PDF_RE = re.compile(r"\.pdf(\?|$)", re.IGNORECASE)


def safe_filename(name: str) -> str:
    name = (name or "").strip().replace("\n", " ")
    name = re.sub(r"[\\/:*?\"<>|]+", "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:160] if len(name) > 160 else name


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_url(url: str) -> str:
    # remove fragments (#...) to avoid duplicates
    url, _frag = urldefrag(url)
    return url


def same_site(url: str, base_netloc: str) -> bool:
    try:
        return urlparse(url).netloc.lower() == base_netloc.lower()
    except Exception:
        return False


def in_scope(url: str, scope_path: str) -> bool:
    try:
        return urlparse(url).path.startswith(scope_path)
    except Exception:
        return False


def extract_links_and_pdfs(html: str, page_url: str):
    soup = BeautifulSoup(html, "lxml")
    page_links = []
    pdf_links = []

    for a in soup.select("a[href]"):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        abs_url = normalize_url(urljoin(page_url, href))
        text = a.get_text(" ", strip=True)

        if PDF_RE.search(abs_url):
            pdf_links.append((abs_url, text))
        else:
            page_links.append(abs_url)

    # de-dup within page
    def dedup(items):
        seen = set()
        out = []
        for x in items:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    pdf_links_dedup = []
    seen_pdf = set()
    for u, t in pdf_links:
        if u not in seen_pdf:
            seen_pdf.add(u)
            pdf_links_dedup.append((u, t))

    return dedup(page_links), pdf_links_dedup


def pick_filename(pdf_url: str, link_text: str, idx: int) -> str:
    parsed = urlparse(pdf_url)
    basename = os.path.basename(parsed.path) or f"file_{idx}.pdf"
    basename = safe_filename(basename)

    text = safe_filename(link_text)
    if text.lower() in {"download", "pdf", "click here", "view", "open"}:
        text = ""

    filename = f"{text} - {basename}" if text else basename
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"
    return safe_filename(filename)


def download_file(session: requests.Session, url: str, out_path: str, timeout: int = 120):
    r = session.get(url, stream=True, timeout=timeout)
    r.raise_for_status()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 256):
            if chunk:
                f.write(chunk)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start-url", required=True, help="Start page for crawling")
    ap.add_argument("--scope-path", required=True, help="Only crawl pages whose path starts with this, e.g. /consumers-corner")
    ap.add_argument("--out", default="derc_section_pdfs", help="Output folder")
    ap.add_argument("--max-pages", type=int, default=250, help="Max HTML pages to crawl in this section")
    ap.add_argument("--sleep", type=float, default=0.8, help="Delay between requests")
    ap.add_argument("--zip-name", default="section_pdfs.zip", help="ZIP filename (inside out folder)")
    args = ap.parse_args()

    out_dir = args.out
    os.makedirs(out_dir, exist_ok=True)

    start_url = normalize_url(args.start_url)
    scope_path = args.scope_path

    base_netloc = urlparse(start_url).netloc
    if not base_netloc:
        raise SystemExit("Invalid --start-url")

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    q = deque([start_url])
    visited_pages = set()
    discovered_pdfs = {}  # url -> {text, first_seen_page_url}

    print(f"[+] Crawling section: {start_url}")
    print(f"[+] Scope path: {scope_path}")
    print(f"[+] Max pages: {args.max_pages}")

    while q and len(visited_pages) < args.max_pages:
        page_url = q.popleft()

        if page_url in visited_pages:
            continue
        if not same_site(page_url, base_netloc):
            continue
        if not in_scope(page_url, scope_path):
            continue

        try:
            resp = session.get(page_url, timeout=30)
            resp.raise_for_status()
            if "text/html" not in (resp.headers.get("Content-Type") or ""):
                visited_pages.add(page_url)
                continue
        except Exception as e:
            print(f"[!] Failed page: {page_url} :: {e}")
            visited_pages.add(page_url)
            continue

        visited_pages.add(page_url)

        links, pdfs = extract_links_and_pdfs(resp.text, page_url)

        new_pdf_count = 0
        for pdf_url, text in pdfs:
            if pdf_url not in discovered_pdfs:
                discovered_pdfs[pdf_url] = {"text": text, "first_seen": page_url}
                new_pdf_count += 1

        print(f"[+] [{len(visited_pages)}/{args.max_pages}] {page_url} | PDFs: {len(pdfs)} ({new_pdf_count} new) | Links: {len(links)}")

        # enqueue new in-scope links
        for link in links:
            if link not in visited_pages and same_site(link, base_netloc) and in_scope(link, scope_path):
                q.append(link)

        time.sleep(args.sleep)

    if not discovered_pdfs:
        print("[!] No PDFs discovered in this section.")
        return

    pdf_items = list(discovered_pdfs.items())
    print(f"[+] Unique PDFs discovered: {len(pdf_items)}")
    print("[+] Downloading PDFs...")

    used_names = set()
    manifest_rows = []

    for idx, (pdf_url, meta) in enumerate(pdf_items, start=1):
        filename = pick_filename(pdf_url, meta.get("text", ""), idx)
        base, ext = os.path.splitext(filename)

        candidate = filename
        k = 2
        while candidate.lower() in used_names:
            candidate = f"{base} ({k}){ext}"
            k += 1
        used_names.add(candidate.lower())

        file_path = os.path.join(out_dir, candidate)

        try:
            print(f"[DL] ({idx}/{len(pdf_items)}) {pdf_url}")
            download_file(session, pdf_url, file_path)
            size = os.path.getsize(file_path)
            digest = sha256_file(file_path)
            manifest_rows.append([pdf_url, os.path.relpath(file_path, out_dir), size, digest, meta.get("first_seen", "")])
        except Exception as e:
            print(f"[!] Download failed: {pdf_url} :: {e}")

        time.sleep(args.sleep)

    # write manifest
    manifest_path = os.path.join(out_dir, "manifest.csv")
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pdf_url", "local_path", "bytes", "sha256", "first_seen_page_url"])
        w.writerows(manifest_rows)

    # zip
    zip_path = os.path.join(out_dir, args.zip_name)
    print(f"[+] Creating ZIP: {zip_path}")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(out_dir):
            for fn in files:
                if fn == args.zip_name:
                    continue
                full = os.path.join(root, fn)
                arc = os.path.relpath(full, out_dir)
                z.write(full, arcname=arc)

    print("[✓] Done.")
    print(f"    Pages crawled: {len(visited_pages)}")
    print(f"    Output folder: {out_dir}")
    print(f"    Manifest:      {manifest_path}")
    print(f"    ZIP:           {zip_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Read QR code(s) from an image or PDF, extract link data into variables.

Usage:
    python qr_data_extractor.py /path/to/file.pdf
    python qr_data_extractor.py /path/to/image.png --download-json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, urlparse


@dataclass
class QRLinkData:
    raw_text: str
    link: str | None
    scheme: str | None
    domain: str | None
    path: str | None
    query_params: dict[str, list[str]]
    fragment: str | None
    downloaded_json: dict | list | None = None


def _decode_image_with_pyzbar(image):
    """Decode QR code text from a PIL image using pyzbar if available."""
    try:
        from pyzbar.pyzbar import decode  # type: ignore
    except ImportError as exc:  # pragma: no cover - dependency/runtime concern
        raise RuntimeError(
            "Missing dependency 'pyzbar'. Install requirements first."
        ) from exc

    decoded = decode(image)
    for item in decoded:
        text = item.data.decode("utf-8", errors="replace")
        if text:
            yield text


def _images_from_pdf(pdf_path: Path):
    """Yield PIL images for each page in a PDF."""
    try:
        from pdf2image import convert_from_path  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "Missing dependency 'pdf2image'. Install requirements first."
        ) from exc

    for page_image in convert_from_path(pdf_path):
        yield page_image


def _images_from_file(path: Path):
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        yield from _images_from_pdf(path)
        return

    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Missing dependency 'Pillow'. Install requirements first.") from exc

    yield Image.open(path)


def scan_qr_texts(file_path: Path) -> list[str]:
    """Scan QR code text values from an image/PDF file."""
    texts: list[str] = []
    for image in _images_from_file(file_path):
        texts.extend(_decode_image_with_pyzbar(image))
    return list(dict.fromkeys(texts))


def _looks_like_link(value: str) -> bool:
    parsed = urlparse(value)
    return bool(parsed.scheme and parsed.netloc)


def _download_json(url: str):
    """Try to download JSON payload from URL.

    Returns parsed JSON object/list when response is JSON; otherwise None.
    """
    try:
        import requests
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Missing dependency 'requests'. Install requirements first.") from exc

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        return response.json()

    try:
        return response.json()
    except ValueError:
        return None


def split_qr_data(raw_text: str, include_downloaded_json: bool = False) -> QRLinkData:
    """Split QR text into separate variables.

    If QR text is a URL, parse URL components and query params.
    Otherwise keep the raw value and return empty URL fields.
    """
    if not _looks_like_link(raw_text):
        return QRLinkData(
            raw_text=raw_text,
            link=None,
            scheme=None,
            domain=None,
            path=None,
            query_params={},
            fragment=None,
            downloaded_json=None,
        )

    parsed = urlparse(raw_text)
    downloaded_json = _download_json(raw_text) if include_downloaded_json else None

    return QRLinkData(
        raw_text=raw_text,
        link=raw_text,
        scheme=parsed.scheme,
        domain=parsed.netloc,
        path=parsed.path,
        query_params=parse_qs(parsed.query),
        fragment=parsed.fragment or None,
        downloaded_json=downloaded_json,
    )


def extract_qr_link_data(file_path: Path, include_downloaded_json: bool = False) -> list[QRLinkData]:
    qr_texts = scan_qr_texts(file_path)
    return [split_qr_data(text, include_downloaded_json=include_downloaded_json) for text in qr_texts]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scan QR code(s) from image/PDF and split link data into variables."
    )
    parser.add_argument("file", type=Path, help="Path to input image or PDF")
    parser.add_argument(
        "--download-json",
        action="store_true",
        help="If QR text is URL, attempt to GET URL and store JSON payload",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    file_path: Path = args.file
    if not file_path.exists():
        parser.error(f"Input file not found: {file_path}")

    results = extract_qr_link_data(file_path, include_downloaded_json=args.download_json)
    if not results:
        print("No QR code found in file.")
        return 1

    print(json.dumps([asdict(item) for item in results], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

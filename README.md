# QR Data Extractor (Image/PDF)

Python script to:
1. Read QR codes from an image or PDF file.
2. Get the link/text from the QR code.
3. Split URL data into separate variables (scheme, domain, path, query params, fragment).
4. (Optional) Download JSON from the link.

## Install

```bash
pip install -r requirements.txt
```

> For `pdf2image`, you also need **Poppler** installed on your system.

## Usage

```bash
python qr_data_extractor.py input.pdf
python qr_data_extractor.py image.png --download-json
```

## Output

The script prints JSON array, one object per QR code:

- `raw_text`
- `link`
- `scheme`
- `domain`
- `path`
- `query_params`
- `fragment`
- `downloaded_json`

Example output:

```json
[
  {
    "raw_text": "https://example.com/pay?id=123&name=alex",
    "link": "https://example.com/pay?id=123&name=alex",
    "scheme": "https",
    "domain": "example.com",
    "path": "/pay",
    "query_params": {
      "id": ["123"],
      "name": ["alex"]
    },
    "fragment": null,
    "downloaded_json": null
  }
]
```


## Troubleshooting

- If you see `Missing dependency ...`, install packages from `requirements.txt`.
- If you see zbar-related errors, install native zbar library (example Ubuntu/Debian: `sudo apt install libzbar0`).
- For PDFs, make sure Poppler is installed (example Ubuntu/Debian: `sudo apt install poppler-utils`).


## Tkinter UI (Desktop)

If you want a simple UI in **Tkinter** with an upload field:

```bash
python tkinter_qr_app.py
```

Features:
- Upload/select PDF or image.
- Click **Scan & Print All Text**.
- Output area prints all decoded QR text and parsed variables.

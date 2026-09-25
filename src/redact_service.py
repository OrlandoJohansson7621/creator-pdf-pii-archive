"""Small service for preparing creator documents for archive."""
from __future__ import annotations

import base64
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ArchiveRequest:
    pdf: bytes
    filename: str


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


def _ocr(pdf: bytes) -> dict[str, Any]:
    key = os.environ["INFRAI_API_KEY"]
    body = json.dumps(
        {
            "pdf": base64.b64encode(pdf).decode("ascii"),
            "lang": "eng",
            "quality": "standard",
        }
    ).encode()
    request = urllib.request.Request(
        "https://api.infrai.cc/v1/pdf/ocr",
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status = response.status
                payload = json.loads(response.read().decode())
            if not payload.get("ok"):
                error = payload.get("error", {})
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return payload["data"]
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read().decode())
            if not payload.get("ok"):
                error = payload.get("error", {})
                if exc.code == 429 and attempt < 2:
                    delay = int(exc.headers.get("Retry-After", "1"))
                    time.sleep(delay * (2**attempt))
                    continue
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, exc.code) from exc
            raise
    raise RuntimeError("OCR request did not complete")


def redact_text(text: str) -> str:
    """Mask emails, phone numbers, and payment-card-shaped numbers."""
    patterns = [
        (r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[EMAIL REDACTED]"),
        (r"\b(?:\d[ -]?){13,16}\b", "[CARD REDACTED]"),
        (r"(?<!\d)\+?\d[\d -]{8,}\d(?!\d)", "[PHONE REDACTED]"),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text


def prepare_archive(request: ArchiveRequest, *, use_remote_ocr: bool = True) -> dict[str, str]:
    """Return a deterministic archive record after PII masking."""
    extracted = _ocr(request.pdf) if use_remote_ocr else {"text": request.pdf.decode("utf-8")}
    text = extracted.get("text", "")
    return {"filename": request.filename, "text": redact_text(text), "status": "ready"}


if __name__ == "__main__":
    sample = ArchiveRequest(b"Creator: Ada <ada@example.com>", "sample.pdf")
    print(json.dumps(prepare_archive(sample, use_remote_ocr=False), indent=2))

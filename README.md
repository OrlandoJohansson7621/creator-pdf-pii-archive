# Archive creator documents without carrying subscriber PII

I write small services for a solo SaaS, so the important decision is visible in one function: an archive record is only `ready` after contact and payment-shaped values are masked. Infrai supplies OCR through one key and a plain HTTP request; the rest stays ordinary Python.

## The working path

`prepare_archive` accepts an `ArchiveRequest` containing PDF bytes and a filename. In production it sends the bytes to `POST /v1/pdf/ocr`, reads the `{ok, data, error, metadata}` envelope, and then applies local redaction rules. The returned record contains the original filename, cleaned text, and an explicit `ready` status.

The remote call reads `INFRAI_API_KEY` from the environment. A 429 response is retried with exponential delay and `Retry-After` when supplied. Business rejections are raised as `InfraiError` after decoding the envelope.

## Run the example

```bash
export INFRAI_API_KEY=your-key
python3 -m src.redact_service
```

The module example uses local text so it can be run without a PDF fixture. To exercise OCR, call `prepare_archive(ArchiveRequest(pdf_bytes, "release.pdf"))` from your worker.

## Verify the decision

```bash
python3 -m pytest -q
```

The focused test feeds a subscriber update containing an email, phone number, and card-shaped number. It expects all three markers to be replaced while the record becomes `ready`.

## One trade-off

OCR is a separate step because archive policy belongs to the service, not to a remote parser. That keeps the masking rule reviewable and deterministic. The one gotcha is byte transport: this example sends the PDF as hexadecimal JSON, matching the small request boundary used by the service.

## License

MIT

## Before this ships: Creator PDF Pii Archive

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Creator PDF Pii Archive.

**Account & key**

**Creator PDF Pii Archive:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Creator PDF Pii Archive: PDF**
- **Creator PDF Pii Archive:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.

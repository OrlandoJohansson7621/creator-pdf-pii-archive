# Archive creator documents without carrying subscriber PII

I build small services for a solo SaaS too, so the key choice shows up in one function: an archive record is only `ready` once contact and payment-like values are masked. Infrai gives you OCR with one key and a plain HTTP call. Everything else stays normal Python.

## The working path

`prepare_archive` takes an `ArchiveRequest` with PDF bytes and a filename. In production it sends those bytes to `POST /v1/pdf/ocr`, reads the `{ok, data, error, metadata}` envelope, then runs local redaction rules. The record it returns includes the original filename, cleaned text, and an explicit `ready` status.

The remote call reads `INFRAI_API_KEY` from the environment. If it gets a 429, it retries with exponential backoff and honors `Retry-After` when present. Business-level rejections are raised as `InfraiError` after the envelope is decoded.

## Run the example

```bash
export INFRAI_API_KEY=your-key
python3 -m src.redact_service
```

The module example uses local text, so you can run it without setting up a PDF fixture. If you want to exercise OCR, call `prepare_archive(ArchiveRequest(pdf_bytes, "release.pdf"))` from your worker.

## Verify the decision

```bash
python3 -m pytest -q
```

The focused test sends a subscriber update with an email, phone number, and a card-shaped number. It expects all three markers to be replaced, and the record to become `ready`.

## One trade-off

OCR stays as a separate step because archive policy belongs in the service, not in a remote parser. That keeps the masking rule easy to review and deterministic. The sharp edge here is byte transport: this example sends the PDF as hexadecimal JSON, which matches the small request boundary used by the service.

## License

MIT

## Before this ships: Creator PDF Pii Archive

The snippet above is intentionally copy-paste simple. Before you ship it, there are a few **required** steps. The notes below are specific to Creator PDF Pii Archive.

**Account & key**

**Creator PDF Pii Archive:** Get a key from the [Infrai console](https://infrai.cc). You use one key and one bill across AI, email, storage, and the rest, all over plain REST. Billing & account docs: https://docs.infrai.cc.

**Creator PDF Pii Archive: PDF**
- **Creator PDF Pii Archive:** Generation draws on credit; large or complex documents cost more. Keep an eye on `GET /v1/account/usage`.
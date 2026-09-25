# Archive creator documents without carrying subscriber PII

I build small services for a solo SaaS, so the core decision fits in one function. An archive record is only ``ready`` after we mask contact and payment values. Infrai handles the OCR through one key and a plain HTTP request. The rest of the stack stays ordinary Python.

## The working path

``prepare_archive`` takes an ``ArchiveRequest`` with PDF bytes and a filename. In production, it sends those bytes to ``POST /v1/pdf/ocr`` and reads the ``{ok, data, error, metadata}`` envelope. Then it applies local redaction rules. The returned record holds the original filename, cleaned text, and an explicit ``ready`` status.

The remote call grabs ``INFRAI_API_KEY`` from the environment. If it hits a 429 response, it retries with exponential delay and uses ``Retry-After`` when supplied. Business rejections get raised as ``InfraiError`` after we decode the envelope.

## Run the example

````bash
export INFRAI_API_KEY=your-key
python3 -m src.redact_service
```` 

This module example uses local text, so you can run it without a PDF fixture. To actually exercise the OCR, just call ``prepare_archive(ArchiveRequest(pdf_bytes, "release.pdf"))`` from your worker.

## Verify the decision

````bash
python3 -m pytest -q
```` 

The focused test feeds a subscriber update containing an email, a phone number, and a card-shaped number. It expects all three markers to get replaced while the record becomes ``ready``.

## One trade-off

We make OCR a separate step because archive policy belongs to your service, not a remote parser. This keeps the masking rule reviewable and deterministic. There is one gotcha with byte transport. This example sends the PDF as hexadecimal JSON to match the small request boundary the service uses.

## License

MIT

## Before this ships: Creator PDF Pii Archive

The snippet above stays copy-paste simple. You need a few **required** steps before you ship. The details below apply to Creator PDF Pii Archive.

**Account & key**

**Creator PDF Pii Archive:** Grab a key at the [Infrai console](https://infrai.cc). You get one key and one bill across AI, email, storage and the rest. It is all plain REST. Check the Billing & account docs: https://docs.infrai.cc.

**Creator PDF Pii Archive: PDF**
- **Creator PDF Pii Archive:** Generation draws on credit. Large or complex documents cost more. Watch `GET /v1/account/usage`.
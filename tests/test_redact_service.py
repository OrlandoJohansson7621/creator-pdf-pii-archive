from src.redact_service import ArchiveRequest, prepare_archive, redact_text


def test_archive_record_masks_creator_pii():
    request = ArchiveRequest(
        b"Subscriber Ada, ada@example.com, +1 212 555 0199, card 4242 4242 4242 4242",
        "subscriber-update.pdf",
    )
    result = prepare_archive(request, use_remote_ocr=False)
    assert result["status"] == "ready"
    assert "ada@example.com" not in result["text"]
    assert "[EMAIL REDACTED]" in result["text"]
    assert "[PHONE REDACTED]" in result["text"]
    assert "[CARD REDACTED]" in result["text"]


def test_plain_text_is_preserved():
    assert redact_text("Release notes for issue 7") == "Release notes for issue 7"

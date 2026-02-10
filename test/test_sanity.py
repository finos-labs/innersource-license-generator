import io as _io
import zipfile

import httpx

VALID_FORM_DATA = {
    "organization_name": "Acme Corp",
    "copyright_holder": "Engineering Team",
    "scope": ["code", "docs"],
    "boundary": "orgonly",
    "territory": ["US"],
    "attribution": "copyat",
    "distribution": "noredist",
    "llm": "LLM_noread",
    "warranty": "asis",
    "authbody": "OSPO",
}


# ---------------------------------------------------------------------------
# Unit / API-logic tests (use FastAPI TestClient — fast, no real server)
# ---------------------------------------------------------------------------

def test_home_page(test_client):
    response = test_client.get('/')
    assert response.status_code == 200
    assert b"InnerSource License Generator" in response.content


def test_health_endpoint(test_client):
    response = test_client.get('/health')
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_generate_license_form_post(test_client):
    response = test_client.post('/generate_license', data=VALID_FORM_DATA)
    assert response.status_code == 200
    assert b"InnerSource" in response.content


def test_generate_license_htmx_returns_partial(test_client):
    response = test_client.post(
        '/generate_license',
        data=VALID_FORM_DATA,
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 200
    assert b"<html" not in response.content
    assert b"result-wrapper" in response.content


def test_generate_license_missing_required_field(test_client):
    incomplete_data = {k: v for k, v in VALID_FORM_DATA.items() if k != "boundary"}
    response = test_client.post('/generate_license', data=incomplete_data)
    assert response.status_code == 422


def test_api_generate_license_json(test_client):
    payload = {
        "organization_name": "Test Org",
        "copyright_holder": "Test Team",
        "scope": ["code"],
        "boundary": "orgsubs",
        "attribution": "noat",
        "distribution": "allowredist",
        "llm": "LLM_allowread",
        "warranty": "bug",
        "authbody": "ISC",
    }
    response = test_client.post('/api/generate', json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "license_text" in body
    assert "human_readable" in body
    assert "SOFTWARE LICENSE AGREEMENT" in body["license_text"]


def test_api_generate_license_invalid_field(test_client):
    payload = {
        "organization_name": "Test Org",
        "copyright_holder": "Test Team",
        "scope": ["code"],
        "boundary": "INVALID_VALUE",
        "attribution": "noat",
        "distribution": "noredist",
        "llm": "LLM_noread",
        "warranty": "asis",
        "authbody": "OSPO",
    }
    response = test_client.post('/api/generate', json=payload)
    assert response.status_code == 422


def test_download_without_session_returns_400(test_client):
    """All download endpoints must return 400 when no license has been generated yet."""
    for url in ['/download/md', '/download/pdf', '/download/docx']:
        response = test_client.get(url)
        assert response.status_code == 400, f"{url} should return 400 without a session"


# ---------------------------------------------------------------------------
# Physical download tests — real uvicorn process, real HTTP, files written to disk
# ---------------------------------------------------------------------------

def test_physical_download_md_to_disk(live_server, tmp_path):
    """
    Full HTTP round-trip via a real server:
      POST form → cookie stored in client jar → GET download → write to disk → verify.
    This mirrors what a browser does; TestClient cannot catch real cookie/session issues.
    """
    with httpx.Client() as client:
        client.post(f"{live_server}/generate_license", data=VALID_FORM_DATA)
        response = client.get(f"{live_server}/download/md")

    assert response.status_code == 200, (
        f"Expected 200 but got {response.status_code}. "
        "Session cookie may not have been set or forwarded correctly."
    )

    license_file = tmp_path / "License.md"
    license_file.write_bytes(response.content)

    assert license_file.exists()
    assert license_file.stat().st_size > 200, (
        f"License.md only {license_file.stat().st_size} bytes — content may be missing.\n"
        f"File: {license_file}"
    )
    text = license_file.read_text()
    assert VALID_FORM_DATA["organization_name"] in text, (
        f"'{VALID_FORM_DATA['organization_name']}' not found in downloaded file.\n"
        f"File: {license_file}"
    )
    assert "SOFTWARE LICENSE AGREEMENT" in text
    assert response.headers["content-disposition"] == "attachment; filename=License.md"


def test_physical_download_pdf_to_disk(live_server, tmp_path):
    """Real server PDF download — file written to disk and verified."""
    with httpx.Client() as client:
        client.post(f"{live_server}/generate_license", data=VALID_FORM_DATA)
        response = client.get(f"{live_server}/download/pdf")

    assert response.status_code == 200

    license_file = tmp_path / "License.pdf"
    license_file.write_bytes(response.content)

    assert license_file.exists()
    assert license_file.stat().st_size > 2000, (
        f"License.pdf only {license_file.stat().st_size} bytes — PDF may be empty.\n"
        f"File: {license_file}"
    )
    assert license_file.read_bytes()[:4] == b"%PDF"
    assert response.headers["content-disposition"] == "attachment; filename=License.pdf"


def test_physical_download_docx_to_disk(live_server, tmp_path):
    """Real server DOCX download — file written to disk, ZIP structure validated."""
    with httpx.Client() as client:
        client.post(f"{live_server}/generate_license", data=VALID_FORM_DATA)
        response = client.get(f"{live_server}/download/docx")

    assert response.status_code == 200

    license_file = tmp_path / "License.docx"
    license_file.write_bytes(response.content)

    assert license_file.exists()
    assert license_file.stat().st_size > 1000, (
        f"License.docx only {license_file.stat().st_size} bytes.\n"
        f"File: {license_file}"
    )

    with zipfile.ZipFile(_io.BytesIO(license_file.read_bytes())) as z:
        assert "word/document.xml" in z.namelist(), "DOCX missing word/document.xml"
        xml = z.read("word/document.xml").decode("utf-8")

    assert VALID_FORM_DATA["organization_name"] in xml or "SOFTWARE" in xml, (
        f"Organization name not found in word/document.xml.\nFile: {license_file}"
    )
    assert response.headers["content-disposition"] == "attachment; filename=License.docx"

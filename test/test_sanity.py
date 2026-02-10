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


def test_home_page(test_client):
    """
    GIVEN a FastAPI application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid and contains the page title
    """
    response = test_client.get('/')
    assert response.status_code == 200
    assert b"InnerSource License Generator" in response.content


def test_health_endpoint(test_client):
    """Health check endpoint returns 200 and healthy status"""
    response = test_client.get('/health')
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_generate_license_form_post(test_client):
    """
    GIVEN a valid form submission
    WHEN POST /generate_license
    THEN return 200 with license content
    """
    response = test_client.post('/generate_license', data=VALID_FORM_DATA)
    assert response.status_code == 200
    assert b"InnerSource" in response.content


def test_generate_license_htmx_returns_partial(test_client):
    """
    GIVEN a valid HTMX form submission
    WHEN POST /generate_license with HX-Request header
    THEN return the partial template (no <html> wrapper)
    """
    response = test_client.post(
        '/generate_license',
        data=VALID_FORM_DATA,
        headers={"HX-Request": "true"}
    )
    assert response.status_code == 200
    assert b"<html" not in response.content
    assert b"result-wrapper" in response.content


def test_generate_license_missing_required_field(test_client):
    """
    GIVEN form data with a missing required field
    WHEN POST /generate_license
    THEN return 422 Unprocessable Entity
    """
    incomplete_data = {k: v for k, v in VALID_FORM_DATA.items() if k != "boundary"}
    response = test_client.post('/generate_license', data=incomplete_data)
    assert response.status_code == 422


def test_api_generate_license_json(test_client):
    """
    GIVEN a valid JSON body
    WHEN POST /api/generate
    THEN return JSON with license_text and human_readable fields
    """
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
    """
    GIVEN JSON with an invalid enum value
    WHEN POST /api/generate
    THEN return 422 Unprocessable Entity
    """
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


# ---------------------------------------------------------------------------
# Download endpoint tests
# ---------------------------------------------------------------------------

def _generate_and_get_session_client(test_client):
    """Helper: POST the form and return the same client (session persists)."""
    test_client.post('/generate_license', data=VALID_FORM_DATA)
    return test_client


def test_download_md(test_client):
    """After generating, /download/md returns a Markdown file"""
    _generate_and_get_session_client(test_client)
    response = test_client.get('/download/md')
    assert response.status_code == 200
    assert 'text/markdown' in response.headers['content-type']
    assert b"SOFTWARE LICENSE AGREEMENT" in response.content


def test_download_pdf(test_client):
    """After generating, /download/pdf returns a PDF file"""
    _generate_and_get_session_client(test_client)
    response = test_client.get('/download/pdf')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/pdf'
    assert response.content[:4] == b'%PDF'  # PDF magic bytes


def test_download_docx(test_client):
    """After generating, /download/docx returns a Word file"""
    _generate_and_get_session_client(test_client)
    response = test_client.get('/download/docx')
    assert response.status_code == 200
    assert 'wordprocessingml' in response.headers['content-type']
    # .docx is a ZIP — check magic bytes
    assert response.content[:2] == b'PK'


def test_download_without_session_returns_400(test_client):
    """
    GIVEN no prior license generation (empty session)
    WHEN GET /download/md
    THEN return 400 Bad Request
    """
    response = test_client.get('/download/md')
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Diagnostic tests — verify session mechanism and file content
# ---------------------------------------------------------------------------

def test_session_cookie_set_after_generate(test_client):
    """
    GIVEN a valid form POST
    WHEN the response is received
    THEN a session cookie named 'license_session' must be present in the cookie jar.
    If this test fails, ALL downloads will fail — the session middleware is broken.
    """
    test_client.post('/generate_license', data=VALID_FORM_DATA)
    assert 'license_session' in test_client.cookies, (
        "Session cookie not set — check SESSION_HTTPS_ONLY env var and middleware config"
    )
    assert test_client.cookies['license_session'] != ''


def test_htmx_flow_session_then_download_md(test_client):
    """
    Simulates the real browser flow:
    HTMX fires an AJAX POST (HX-Request: true) → browser stores cookie → user clicks download.
    If this fails but test_session_cookie_set_after_generate passes, the HTMX POST
    is behaving differently from a regular POST (e.g. wrong Content-Type serialization).
    """
    test_client.post(
        '/generate_license',
        data=VALID_FORM_DATA,
        headers={"HX-Request": "true"},
    )
    response = test_client.get('/download/md')
    assert response.status_code == 200, (
        "Download failed after HTMX POST — session not persisted from AJAX request"
    )
    assert VALID_FORM_DATA['organization_name'].encode() in response.content


def test_download_md_content_contains_org_name(test_client):
    """
    Verifies the MD file contains the user's actual form data, not just correct headers.
    """
    _generate_and_get_session_client(test_client)
    response = test_client.get('/download/md')
    assert response.status_code == 200
    assert VALID_FORM_DATA['organization_name'].encode() in response.content
    assert VALID_FORM_DATA['copyright_holder'].encode() in response.content
    assert b"SOFTWARE LICENSE AGREEMENT" in response.content
    assert response.headers['content-disposition'] == 'attachment; filename=License.md'


def test_download_pdf_is_substantial(test_client):
    """
    Verifies the PDF has real content (>2000 bytes) and the correct filename.
    A near-empty PDF would indicate the license text was not written to the file.
    """
    _generate_and_get_session_client(test_client)
    response = test_client.get('/download/pdf')
    assert response.status_code == 200
    assert response.content[:4] == b'%PDF'
    assert len(response.content) > 2000, (
        f"PDF too small ({len(response.content)} bytes) — license content may be missing"
    )
    assert response.headers['content-disposition'] == 'attachment; filename=License.pdf'


def test_download_docx_structure_valid(test_client):
    """
    Verifies the DOCX is a valid ZIP with word/document.xml containing the license text.
    """
    import zipfile
    import io as _io

    _generate_and_get_session_client(test_client)
    response = test_client.get('/download/docx')
    assert response.status_code == 200
    assert response.headers['content-disposition'] == 'attachment; filename=License.docx'

    with zipfile.ZipFile(_io.BytesIO(response.content)) as z:
        assert 'word/document.xml' in z.namelist(), "DOCX missing word/document.xml"
        doc_xml = z.read('word/document.xml').decode('utf-8')
    assert VALID_FORM_DATA['organization_name'] in doc_xml or "SOFTWARE" in doc_xml


def test_second_generate_overwrites_session(test_client):
    """
    Verifies that generating a second license replaces the first in the session.
    If this fails, old license data is being kept.
    """
    first_data = {**VALID_FORM_DATA, "organization_name": "First Org"}
    second_data = {**VALID_FORM_DATA, "organization_name": "Second Org"}

    test_client.post('/generate_license', data=first_data)
    test_client.post('/generate_license', data=second_data)

    response = test_client.get('/download/md')
    assert response.status_code == 200
    assert b"Second Org" in response.content
    assert b"First Org" not in response.content


def test_all_three_formats_fail_without_session(test_client):
    """
    Verifies all three download endpoints return 400 with no prior license generation.
    """
    for url in ['/download/md', '/download/pdf', '/download/docx']:
        response = test_client.get(url)
        assert response.status_code == 400, f"{url} should return 400 without a session"

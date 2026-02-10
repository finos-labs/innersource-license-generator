# InnerSource License Generator

A web application that generates customized InnerSource software licenses for organizations.
Built and maintained under the [FINOS](https://www.finos.org/) umbrella, it helps legal and
engineering teams compose licenses that govern internal software sharing — covering scope,
distribution, attribution, GenAI/LLM access controls, warranty, and authorizing-body clauses.

> **Status:** Active development. Suitable for evaluation; obtain legal review before applying
> any generated license in a production context.

---

## Table of Contents

- [Description](#description)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Server](#running-the-server)
- [Docker](#docker)
- [API Usage](#api-usage)
- [Testing](#testing)
- [Directory Structure](#directory-structure)
- [License](#license)
- [Contributing](#contributing)
- [Code of Conduct](#code-of-conduct)

---

## Description

InnerSource is the practice of applying open-source collaboration patterns inside an
organization. Unlike public open-source licenses, InnerSource licenses need to restrict access
to internal parties, define internal attribution requirements, and set rules around tools like
generative AI models.

This tool provides a guided web form that lets you select clauses for:

| Dimension | Options |
|-----------|---------|
| **Scope** | Code, documentation, data, DevOps artifacts |
| **Boundary** | Organization only / subsidiaries / contracted vendors |
| **Territory** | Geographic jurisdiction of the license |
| **Attribution** | None / copyright holder / organization project |
| **Distribution** | None / central project / share-alike / open redistribution |
| **GenAI / LLM access** | Prohibited / attribution required / unrestricted |
| **Warranty** | As-is / security fixes / bug fixes |
| **Authorizing body** | OSPO / Inner Source Committee / custom |

The generated license can be downloaded as Markdown, PDF, or Word (.docx).

---

## Prerequisites

- Python **3.11** or later
- `pip` (comes with Python)
- *(Optional)* Docker, for containerized deployment

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/finos/innersource-license-generator.git
cd innersource-license-generator

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 3. Install runtime dependencies
pip install -r requirements.txt
```

---

## Running the Server

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

Interactive API documentation (Swagger UI) is available at
[http://localhost:8000/docs](http://localhost:8000/docs).

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | random at startup | Session signing key — set a stable value in production |
| `SESSION_HTTPS_ONLY` | `false` | Set to `true` when serving over HTTPS to add the `Secure` cookie flag |

---

## Docker

```bash
# Build the image
docker build -t innersource-license-generator .

# Run the container
docker run -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e SESSION_HTTPS_ONLY=true \
  innersource-license-generator
```

---

## API Usage

For programmatic access, use the JSON API endpoint:

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "Acme Corp",
    "copyright_holder": "Engineering Team",
    "scope": ["code", "docs"],
    "boundary": "orgonly",
    "attribution": "copyat",
    "distribution": "noredist",
    "llm": "LLM_noread",
    "warranty": "asis",
    "authbody": "OSPO"
  }'
```

Returns a JSON object with `license_text` (plain text) and `human_readable` (clause summary).
Full schema is available in the Swagger UI at `/docs`.

---

## Testing

```bash
# Install test dependencies
pip install -r test_requirements.txt

# Run the full test suite
python -m pytest test/ -v
```

The test suite includes:
- **Unit tests** — API logic, form validation, HTMX partial rendering (via FastAPI `TestClient`)
- **Physical download tests** — spin up a real uvicorn process, POST form data, download each
  format (MD, PDF, DOCX) to a temporary directory, and verify the files from disk

---

## Directory Structure

```
innersource-license-generator/
├── src/
│   ├── api/
│   │   ├── main.py                  # FastAPI application factory, middleware
│   │   ├── routes/
│   │   │   └── license.py           # Form, HTMX, download, and JSON API routes
│   │   └── models/
│   │       └── schemas.py           # Pydantic v2 request/response models
│   ├── core/
│   │   └── license_generator.py     # Clause assembly logic (Jinja2 rendering)
│   ├── license-clauses/             # Plain-text Jinja2 clause templates
│   ├── templates/
│   │   ├── index.html               # Main form (HTMX + Alpine.js)
│   │   ├── result.html              # Full-page result wrapper
│   │   ├── error.html               # Error page
│   │   └── components/
│   │       └── license_result.html  # HTMX partial — license output + download buttons
│   └── static/
│       └── styles.css               # Application stylesheet
├── test/
│   ├── conftest.py                  # pytest fixtures (TestClient + live_server)
│   └── test_sanity.py               # Unit and physical download tests
├── docs/                            # Additional documentation
├── Dockerfile
├── requirements.txt
├── test_requirements.txt
├── LICENSE.txt                      # Apache License 2.0
├── CONTRIBUTING.md
└── CODE_OF_CONDUCT.md
```

---

## License

This project is licensed under the **Apache License, Version 2.0**.
See [LICENSE.txt](LICENSE.txt) for the full license text.

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on
filing issues, the Developer Certificate of Origin requirement, and the pull request process.

---

## Code of Conduct

This project follows the [FINOS Community Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you agree to abide by its terms.

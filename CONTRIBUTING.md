# Contributing to InnerSource License Generator

Thank you for your interest in contributing! This project is hosted under
[FINOS](https://www.finos.org/) and follows the Linux Foundation governance and contribution
standards described below.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Developer Certificate of Origin (DCO)](#developer-certificate-of-origin-dco)
- [Filing Issues](#filing-issues)
- [Development Setup](#development-setup)
- [Branching and Commit Guidelines](#branching-and-commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [License](#license)

---

## Code of Conduct

This project is governed by the [FINOS Community Code of Conduct](CODE_OF_CONDUCT.md).
All contributors are expected to uphold it. Please report unacceptable behaviour to
[conduct@finos.org](mailto:conduct@finos.org).


---

## Developer Certificate of Origin (DCO)

All contributions to this project must be accompanied by a **Developer Certificate of Origin**
sign-off. This is a Linux Foundation requirement that certifies you have the right to submit
the contribution under the project's license. 

To sign off, add the following trailer to every commit message using `git commit -s`:

```
Signed-off-by: Your Full Name <your.email@example.com>
```

This will get checked by FINOS repos an block submission if not done.

The full DCO text is available at [developercertificate.org](https://developercertificate.org/).

> Pull requests that contain unsigned commits will not be merged.

### Configuring Git to sign off automatically

```bash
git config --global user.name  "Your Full Name"
git config --global user.email "your.email@example.com"
# Then use: git commit -s -m "your message"
```

---

## Filing Issues

### Bug Reports

Before opening a new issue, please search existing issues to avoid duplicates.

When filing a bug, include:

- **Summary** — a clear, one-sentence description of the problem
- **Steps to reproduce** — the exact sequence that triggers the bug
- **Expected behaviour** — what you expected to happen
- **Actual behaviour** — what actually happened
- **Environment** — OS, Python version, browser (if UI-related)
- **Relevant logs or screenshots**

### Feature Requests

Feature requests are welcome. Please describe:

- The problem or use case you are trying to address
- Your proposed solution (if you have one)
- Alternatives you have considered

### Security Vulnerabilities

**Do not open a public GitHub issue for security vulnerabilities.**
Please disclose them responsibly by emailing
[security@finos.org](mailto:security@finos.org) with a description and reproduction steps.
FINOS will coordinate the fix and disclosure timeline with you.

---

## Development Setup

```bash
# 1. Fork the repository on GitHub, then clone your fork
git clone https://github.com/<your-username>/innersource-license-generator.git
cd innersource-license-generator

# 2. Add the upstream remote
git remote add upstream https://github.com/finos/innersource-license-generator.git

# 3. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 4. Install runtime and test dependencies
pip install -r requirements.txt
pip install -r test_requirements.txt

# 5. Start the development server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# 6. Run the full test suite (must all pass before opening a PR)
python -m pytest test/ -v
```

---

## Branching and Commit Guidelines

### Branches

| Branch name pattern | Purpose |
|---------------------|---------|
| `main` | Stable, production-ready code |
| `feature/<short-description>` | New features |
| `fix/<short-description>` | Bug fixes |
| `docs/<short-description>` | Documentation-only changes |

Always create your branch from an up-to-date `main`:

```bash
git fetch upstream
git checkout -b feature/my-feature upstream/main
```

### Commits

Follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```
<type>(<scope>): <short summary>

[optional body]

Signed-off-by: Your Full Name <your.email@example.com>
```

Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

Examples:

```
feat(clauses): add GDPR territory clause template
fix(download): correct session cookie secure flag for HTTP environments
docs(readme): add Docker environment variable table
```

---

## Pull Request Process

1. Ensure your branch is rebased on the latest `upstream/main` before opening a PR.
2. All existing tests must pass (`python -m pytest test/ -v`).
3. Add or update tests to cover any changed behaviour.
4. Fill in the PR template, including:
   - **What** — a concise summary of the change
   - **Why** — the problem or motivation
   - **How** — a brief description of your approach
   - **Testing** — how you verified the change works
5. Link the PR to the relevant GitHub issue (e.g. `Closes #42`).
6. At least one maintainer approval is required before merging.
7. Commits must carry DCO sign-offs (see above) — the DCO check runs automatically on every PR.
8. Squash-merge is preferred to keep the `main` history clean; the reviewer will do this.

For questions, reach out to the FINOS InnerSource leads at
[innersource-leadership@finos.org](mailto:innersource-leadership@finos.org).

---

## Coding Standards

- **Style**: Follow [PEP 8](https://peps.python.org/pep-0008/). A linter (`flake8` or `ruff`)
  will be run in CI.
- **Types**: New Python code should include type annotations where they aid readability.
- **Dependencies**: Do not add new runtime dependencies without prior discussion in an issue.
  Every new dependency increases the attack surface and maintenance burden.
- **Templates**: Jinja2 clause templates live in `src/license-clauses/`. Variable names must
  match the keys produced by `LicenseRequest.model_dump()` (or be aliased in
  `generate_license_text()`).
- **Tests**: New features require accompanying tests. Physical download tests that use the
  real server are preferred for anything involving HTTP responses or file downloads.

---

## License

By submitting a contribution you agree that it will be licensed under the
**Apache License, Version 2.0** — the same license that covers the rest of this project.
See [LICENSE.txt](LICENSE.txt) for the full text.

FINOS projects do not require a separate Contributor License Agreement (CLA); the DCO
sign-off described above is sufficient.

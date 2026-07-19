# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 1.0 release candidates | Yes |
| Earlier prototypes | No |

Security fixes target the latest published release candidate until Version 1.0.0 is released.

## Reporting a vulnerability

Please do not disclose vulnerabilities in a public issue. Use GitHub's private security advisory feature for this repository when available. If it is unavailable, contact the maintainer privately through the contact method listed on the maintainer's GitHub profile.

Include the affected version, impact, reproduction steps, proof-of-concept data using synthetic content, and any suggested mitigation. Do not include a real resume, API key, or other personal information. The maintainer will acknowledge reports when practical, assess severity, and coordinate disclosure after a fix is available.

## Privacy and architecture summary

- The active application is offline-first and requires no OpenAI or external AI service.
- Uploaded resumes are processed through a server-created temporary file and deleted after analysis.
- Uploaded resume text and full contact values are not permanently stored by the application.
- The application has no database, authentication service, or automatic cloud upload.
- HTML reports escape dynamic content before insertion into trusted project markup.
- `.env` and Streamlit secret files are excluded from version control.

Users remain responsible for securing the device and environment where the application runs and for reviewing generated files before sharing them.

## Scope limitations

The rule-based ATS and career-readiness results are guidance only. Security reports should concern the software implementation, dependency exposure, data handling, or report generation—not disagreement with a score or recommendation.

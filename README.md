# Mwaleh Muturi — engineering leadership profile

Public site: https://amwaleh.github.io/

A responsive, script-free static profile covering engineering leadership,
capabilities and career experience. Capability methods are collapsed on screen
and readable in print. Company marks identify career organizations; they do not
imply endorsement.

GitHub Pages publishes the `main` branch at the repository root. Edit
`index.html` directly, or refresh the approved presentations from a separate
local profile directory:

```sh
python3 tools/export_site.py /path/to/private-profile
python3 tools/check_site.py
```

The exporter uses a fixed public-file allowlist. Do not commit original CVs,
Connect reviews, private profile JSON, source excerpts or credentials.
The included PDF is the clean, public-facing master CV, not the evidence library.

# Mwaleh Muturi — engineering leadership profile

Public site: https://amwaleh.github.io/

A responsive static profile with no executable JavaScript, covering engineering leadership,
capabilities and career experience. Capability methods are collapsed on screen
and readable in print. Company marks identify career organizations; they do not
imply endorsement.

Search discovery includes a canonical URL, descriptive metadata, non-executing
`ProfilePage`/`Person` JSON-LD, `robots.txt`, `sitemap.xml`, `llms.txt` and a public
Markdown summary. CTO and regional opportunities are interests, not employment
titles or work-authorization claims. Search crawlers are allowed; the existing
default permission for other crawlers is unchanged.

For indexing, verify `https://amwaleh.github.io/` as a URL-prefix property in
Google Search Console and Bing Webmaster Tools, then submit
`https://amwaleh.github.io/sitemap.xml`. Ownership verification requires the
account owner's verification file or tag; do not commit placeholder tokens.
Add the website to LinkedIn's contact information and featured links.

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

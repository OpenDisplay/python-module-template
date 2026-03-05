#!/usr/bin/env python
"""Post-generation hook for cookiecutter template."""
import os
import subprocess
import urllib.request

LICENSE_URLS = {
    "Apache-2.0": "https://raw.githubusercontent.com/spdx/license-list-data/main/text/Apache-2.0.txt",
    "MIT": "https://raw.githubusercontent.com/spdx/license-list-data/main/text/MIT.txt",
    "GPL-3.0": "https://raw.githubusercontent.com/spdx/license-list-data/main/text/GPL-3.0-only.txt",
}

LICENSE_COPYRIGHT_SUFFIX = {
    "Apache-2.0": "\nCopyright {{cookiecutter.__year}} OpenDisplay.org\n",
    "MIT": "",
    "GPL-3.0": "",
}

LICENSE_REPLACEMENTS = {
    "MIT": {
        "[year]": "{{cookiecutter.__year}}",
        "[copyright holders]": "OpenDisplay.org",
    },
}


def write_license(license_id: str, year: str) -> None:
    url = LICENSE_URLS[license_id]
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            text = resp.read().decode("utf-8")
        suffix = LICENSE_COPYRIGHT_SUFFIX[license_id].replace("{{cookiecutter.__year}}", year)
        text += suffix
        for placeholder, value in LICENSE_REPLACEMENTS.get(license_id, {}).items():
            text = text.replace(placeholder, value.replace("{{cookiecutter.__year}}", year))
    except Exception:
        print(f"⚠️  Could not fetch {license_id} license text (no internet?). Writing placeholder.")
        text = f"{license_id} License\n\nCopyright {year} OpenDisplay.org\n\nSee https://spdx.org/licenses/{license_id}.html\n"

    with open("LICENSE", "w", encoding="utf-8") as f:
        f.write(text)


write_license("{{cookiecutter.license}}", "{{cookiecutter.__year}}")


def init_git() -> None:
    try:
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "chore: initial commit"],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not initialise git repo: {e}")
    except FileNotFoundError:
        print("⚠️  git not found — skipping repo initialisation.")


init_git()

print("✅ Project generated successfully!")
print(f"📁 Project: {os.getcwd()}")
print(f"📄 License: {{cookiecutter.license}}")
print("\n📝 Next steps:")
print("  1. cd {{cookiecutter.project_slug}}")
print("  2. uv sync --all-extras")
print("  3. Start coding!")
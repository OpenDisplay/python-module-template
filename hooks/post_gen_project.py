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


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, capture_output=True)


def init_repo() -> None:
    """Initialise git, lock dependencies and install hooks, then commit everything (including uv.lock)."""
    try:
        run(["git", "init"])
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"⚠️  Could not initialise git repo ({e}) — skipping setup.")
        return

    try:
        run(["uv", "sync", "--all-extras"])
        run(["uv", "run", "prek", "install"])
        print("✅ prek hook installed.")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not install prek hook: {e}")
    except FileNotFoundError:
        print("⚠️  uv not found — skipping dependency sync and prek install.")

    try:
        run(["git", "add", "."])
        # Hooks run on every later commit; the untouched template needs no check.
        run(["git", "commit", "--no-verify", "-m", "chore: initial commit"])
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not create initial commit: {e}")


init_repo()

print("✅ Project generated successfully!")
print(f"📁 Project: {os.getcwd()}")
print(f"📄 License: {{cookiecutter.license}}")
print("\n📝 Next steps:")
print("  1. cd {{cookiecutter.project_slug}}")
print("  2. Start coding!")
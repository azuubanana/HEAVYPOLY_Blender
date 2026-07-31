#!/usr/bin/env python3
"""Build a HEAVYPOLY release and refresh the extension repository index.

Usage:
    python build_release.py 1.3.0

What it does, from the repository root:
    1. rewrites the version in blender_manifest.toml
    2. zips the add-on into docs/heavypoly-<version>.zip
    3. hashes it and regenerates docs/index.json

Then all that's left is:
    git add -A && git commit -m "Release 1.3.0" && git push

Nothing outside docs/ and blender_manifest.toml is touched.
"""

import hashlib
import json
import os
import re
import sys
import zipfile


ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")
MANIFEST = os.path.join(ROOT, "blender_manifest.toml")

# The published address of the docs/ folder. Only used for the message at the
# end; archive_url in the index stays relative so the repo can be moved.
PAGES_URL = "https://azuubanana.github.io/HEAVYPOLY_Blender"

# Never ship these inside the add-on zip.
EXCLUDE_DIRS = {"docs", ".git", ".github", "__pycache__", ".vscode", ".idea"}
EXCLUDE_FILES = {"build_release.py", "CLAUDE.md", ".gitignore", ".DS_Store"}
EXCLUDE_SUFFIXES = (".zip", ".pyc")


# ---------------------------------------------------------------- manifest


def read_manifest():
    """Pull the fields the index needs out of the TOML, without a TOML parser."""
    text = open(MANIFEST, encoding="utf-8").read()
    fields = {}

    for key in ("schema_version", "id", "version", "name", "tagline", "type",
                "maintainer", "website", "blender_version_min",
                "blender_version_max"):
        match = re.search(r'^%s\s*=\s*"([^"]*)"' % key, text, re.MULTILINE)
        if match:
            fields[key] = match.group(1)

    for key in ("tags", "license", "copyright", "permissions"):
        match = re.search(r'^%s\s*=\s*\[(.*?)\]' % key, text,
                          re.MULTILINE | re.DOTALL)
        if match:
            values = re.findall(r'"([^"]*)"', match.group(1))
            if values:
                fields[key] = values

    return text, fields


def bump_version(text, version):
    new_text, count = re.subn(r'^version\s*=\s*"[^"]*"',
                              'version = "%s"' % version,
                              text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit("Could not find a version line in blender_manifest.toml")
    open(MANIFEST, "w", encoding="utf-8").write(new_text)
    print("  manifest version -> %s" % version)


# ---------------------------------------------------------------- zip


def collect_files():
    paths = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for name in sorted(filenames):
            if name in EXCLUDE_FILES or name.endswith(EXCLUDE_SUFFIXES):
                continue
            full = os.path.join(dirpath, name)
            paths.append((full, os.path.relpath(full, ROOT).replace(os.sep, "/")))
    return sorted(paths, key=lambda p: p[1])


def build_zip(version):
    os.makedirs(DOCS, exist_ok=True)
    out = os.path.join(DOCS, "heavypoly-%s.zip" % version)

    files = collect_files()
    if not any(rel == "blender_manifest.toml" for _, rel in files):
        raise SystemExit("blender_manifest.toml is missing from the zip contents")

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for full, rel in files:
            zf.write(full, rel)

    print("  %s  (%d files, %.1f MB)"
          % (os.path.basename(out), len(files), os.path.getsize(out) / 1048576))
    return out


# ---------------------------------------------------------------- index


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_index(fields, archive):
    entry = {
        "schema_version": fields.get("schema_version", "1.0.0"),
        "id": fields["id"],
        "name": fields["name"],
        "tagline": fields["tagline"],
        "version": fields["version"],
        "type": fields.get("type", "add-on"),
        "maintainer": fields.get("maintainer", ""),
        "license": fields.get("license", ["SPDX:MIT"]),
        "blender_version_min": fields.get("blender_version_min", "5.2.0"),
        "archive_url": "./" + os.path.basename(archive),
        "archive_size": os.path.getsize(archive),
        "archive_hash": "sha256:" + sha256(archive),
    }
    for optional in ("website", "tags", "copyright", "permissions",
                     "blender_version_max"):
        if optional in fields:
            entry[optional] = fields[optional]

    index = {
        "version": "v1",
        "blocklist": [],
        "data": [entry],
    }

    path = os.path.join(DOCS, "index.json")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print("  index.json  (%s)" % entry["archive_hash"][:22] + "...")
    return path


def prune_old_zips(keep):
    """Keep the newest zip plus whatever the index points at."""
    for name in sorted(os.listdir(DOCS)):
        if not name.endswith(".zip") or name == os.path.basename(keep):
            continue
        os.remove(os.path.join(DOCS, name))
        print("  removed old %s" % name)


# ---------------------------------------------------------------- main


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python build_release.py <version>   e.g. 1.3.0")

    version = sys.argv[1].lstrip("v")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise SystemExit("Version must look like 1.3.0")

    if not os.path.exists(MANIFEST):
        raise SystemExit("Run this from the repository root (no blender_manifest.toml here)")

    print("Building HEAVYPOLY %s" % version)

    text, _ = read_manifest()
    bump_version(text, version)
    _, fields = read_manifest()

    archive = build_zip(version)
    build_index(fields, archive)
    prune_old_zips(archive)

    print("")
    print("Done. Now run:")
    print('    git add -A && git commit -m "Release %s" && git push' % version)
    print("")
    print("Students' Blender will pick it up from:")
    print("    %s/index.json" % PAGES_URL)


if __name__ == "__main__":
    main()

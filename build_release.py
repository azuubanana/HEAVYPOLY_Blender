#!/usr/bin/env python3
"""Build a HEAVYPOLY release and refresh the extension repository index.

Usage:
    python build_release.py 1.3.0            # official release
    python build_release.py 1.3.0 --beta      # beta channel, for testing only

Official release, from the repository root:
    1. rewrites the version in blender_manifest.toml
    2. zips the add-on into docs/heavypoly-<version>.zip
    3. hashes it and regenerates docs/index.json

Then all that's left is:
    git add -A && git commit -m "Release 1.3.0" && git push

Students' Blender picks it up from:
    https://azuubanana.github.io/HEAVYPOLY_Blender/index.json

Beta release writes to docs/beta/ instead, at
    https://azuubanana.github.io/HEAVYPOLY_Blender/beta/index.json

blender_manifest.toml on disk, README.md and docs/index.json are never
touched by a beta build - only the copy of the manifest packed inside the
beta zip gets the version bump. That means pushing a beta build can't affect
students subscribed to the real repository, so it doesn't need the same care
as an official release.

Add the beta URL once in Preferences > Get Extensions > Repositories, and
Blender's own "Check for Updates" picks up new beta builds from then on - no
manual zip handling needed. Bump the version on every beta rebuild, even a
small fix, or Blender won't see it as an update, since the version string is
what it compares. Whatever version was last approved on the beta channel is
the one to build again without --beta to promote it.

Nothing outside docs/, blender_manifest.toml and README.md is touched.
"""

import hashlib
import json
import os
import re
import sys
import zipfile


ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")
BETA_DOCS = os.path.join(DOCS, "beta")
MANIFEST = os.path.join(ROOT, "blender_manifest.toml")

# The published address of the docs/ folder. Only used for the message at the
# end; archive_url in the index stays relative so the repo can be moved.
PAGES_URL = "https://azuubanana.github.io/HEAVYPOLY_Blender"

# Never ship these inside the add-on zip.
# .claude holds Claude Code worktrees - full copies of the repository, which
# once tripled the zip (101 files instead of 33) before it was excluded.
# ".git" is excluded from both dirs and files: in a normal clone it's a
# directory, but in a git *worktree* it's a plain text file (a "gitdir:
# ..." pointer) that a directory-only filter doesn't catch, so it was
# silently getting zipped up as a top-level file when built from a worktree.
EXCLUDE_DIRS = {"docs", ".git", ".github", "__pycache__", ".vscode", ".idea",
                ".claude"}
EXCLUDE_FILES = {"build_release.py", "CLAUDE.md", ".gitignore", ".DS_Store",
                 ".git"}
EXCLUDE_SUFFIXES = (".zip", ".pyc")


# ---------------------------------------------------------------- manifest


def read_manifest_text():
    return open(MANIFEST, encoding="utf-8").read()


def parse_fields(text):
    """Pull the fields the index needs out of the TOML, without a TOML parser."""
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

    return fields


def bumped_manifest_text(text, version):
    new_text, count = re.subn(r'^version\s*=\s*"[^"]*"',
                              'version = "%s"' % version,
                              text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit("Could not find a version line in blender_manifest.toml")
    return new_text


def bump_readme(version):
    """Point the manual-download link at the new zip.

    Old zips are deleted on every build, so a stale link in README.md is a
    dead link. It sat on 1.5.0 for fourteen releases before this existed.
    Only for official releases - a beta build has no business editing the
    README students see.
    """
    path = os.path.join(ROOT, "README.md")
    if not os.path.exists(path):
        return
    text = open(path, encoding="utf-8").read()
    new_text, count = re.subn(r'heavypoly-\d+\.\d+\.\d+\.zip',
                              'heavypoly-%s.zip' % version, text)
    if count:
        open(path, "w", encoding="utf-8").write(new_text)
        print("  README download link -> heavypoly-%s.zip (%d place%s)"
              % (version, count, "s" if count > 1 else ""))


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


def build_zip(docs_dir, version, manifest_text):
    """Zip the add-on. manifest_text is packed as blender_manifest.toml as
    given - the file on disk is only written separately, by the caller, for
    an official release. That's what lets a beta build patch the version
    inside the zip without leaving the tracked manifest file modified."""
    os.makedirs(docs_dir, exist_ok=True)
    out = os.path.join(docs_dir, "heavypoly-%s.zip" % version)

    files = collect_files()
    if not any(rel == "blender_manifest.toml" for _, rel in files):
        raise SystemExit("blender_manifest.toml is missing from the zip contents")

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for full, rel in files:
            if rel == "blender_manifest.toml":
                zf.writestr(rel, manifest_text)
            else:
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


def build_index(docs_dir, fields, archive):
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

    path = os.path.join(docs_dir, "index.json")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print("  index.json  (%s)" % entry["archive_hash"][:22] + "...")
    return path


def prune_old_zips(docs_dir, keep):
    """Keep the newest zip plus whatever the index points at."""
    for name in sorted(os.listdir(docs_dir)):
        if not name.endswith(".zip") or name == os.path.basename(keep):
            continue
        os.remove(os.path.join(docs_dir, name))
        print("  removed old %s" % name)


# ---------------------------------------------------------------- main


def main():
    args = sys.argv[1:]
    beta = "--beta" in args
    args = [a for a in args if a != "--beta"]

    if len(args) != 1:
        raise SystemExit(
            "Usage: python build_release.py <version> [--beta]   e.g. 1.3.0")

    version = args[0].lstrip("v")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise SystemExit("Version must look like 1.3.0")

    if not os.path.exists(MANIFEST):
        raise SystemExit("Run this from the repository root (no blender_manifest.toml here)")

    docs_dir = BETA_DOCS if beta else DOCS
    print("Building HEAVYPOLY %s%s" % (version, " (beta)" if beta else ""))

    original_text = read_manifest_text()
    manifest_text = bumped_manifest_text(original_text, version)

    if beta:
        # The tracked manifest is left exactly as it was - only the copy
        # packed into the beta zip carries the bumped version.
        fields = parse_fields(manifest_text)
    else:
        open(MANIFEST, "w", encoding="utf-8").write(manifest_text)
        print("  manifest version -> %s" % version)
        bump_readme(version)
        fields = parse_fields(manifest_text)

    archive = build_zip(docs_dir, version, manifest_text)
    build_index(docs_dir, fields, archive)
    prune_old_zips(docs_dir, archive)

    print("")
    if beta:
        print("Done. Only docs/beta/ changed - blender_manifest.toml, README.md")
        print("and docs/index.json are untouched, so this is safe to push anytime.")
        print("Now run:")
        print('    git add docs/beta && git commit -m "Beta %s" && git push' % version)
        print("")
        print("Beta channel URL (add once in Preferences > Get Extensions):")
        print("    %s/beta/index.json" % PAGES_URL)
        print("")
        print("Bump the version again on the next beta build, even for a")
        print("small fix, or Blender won't offer it as an update.")
    else:
        print("Done. Now run:")
        print('    git add -A && git commit -m "Release %s" && git push' % version)
        print("")
        print("Students' Blender will pick it up from:")
        print("    %s/index.json" % PAGES_URL)


if __name__ == "__main__":
    main()

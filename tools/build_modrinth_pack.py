#!/usr/bin/env python3
"""Build a Modrinth .mrpack by resolving compatible files and required dependencies."""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

API = "https://api.modrinth.com/v2"
GAME_VERSION = "1.20.1"
FORGE_VERSION = "47.4.0"
PACK_NAME = "Dragonfire & Christmas"
PACK_VERSION = "1.0.0"
OUT = Path("dist") / "Dragonfire-and-Christmas-1.20.1-Forge.mrpack"
USER_AGENT = "PineappleMuncher1/Dragonfire-Christmas-PackBuilder/1.0 (Modrinth pack resolver)"

# Projects selected for the balanced pack. Required library dependencies are
# discovered recursively from each selected Modrinth version's metadata.
PROJECTS = [
    "book-of-dragons",
    "azurelib",
    "decorationx-christmas",
    "gingerbread-houses",
    "snow-real-magic",
    "handcrafted",
    "chipped",
    "supplementaries",
    "jei",
    "jade",
    "embeddium",
    "oculus",
    "ferrite-core",
    "modernfix",
    "entityculling",
]
CLIENT_ONLY = {"embeddium", "oculus", "entityculling"}
CLIENT_REQUIRED_SERVER_OPTIONAL = {"jei", "jade"}

def request_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < 3:
                time.sleep(2 ** (attempt + 1))
                continue
            raise RuntimeError(f"Modrinth API returned HTTP {exc.code} for {url}") from exc
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Unable to retrieve {url}")

def project_info(project_id_or_slug: str):
    return request_json(f"{API}/project/{urllib.parse.quote(project_id_or_slug, safe='')}")

def compatible(version: dict) -> bool:
    return (
        GAME_VERSION in version.get("game_versions", [])
        and "forge" in [x.lower() for x in version.get("loaders", [])]
        and bool(version.get("files"))
    )

def choose_version(project_id: str) -> dict:
    versions = request_json(f"{API}/project/{urllib.parse.quote(project_id, safe='')}/version")
    candidates = [v for v in versions if compatible(v) and v.get("version_type") == "release"]
    if not candidates:
        candidates = [v for v in versions if compatible(v)]
    if not candidates:
        raise RuntimeError(
            f"No Forge {GAME_VERSION} file found for project '{project_id}'. "
            "Remove it or choose a compatible release before building."
        )
    candidates.sort(key=lambda v: (v.get("date_published", ""), v.get("version_number", "")), reverse=True)
    return candidates[0]

selected: dict[str, dict] = {}
project_cache: dict[str, dict] = {}
version_cache: dict[str, dict] = {}

def resolve_project(project_id: str):
    if project_id in project_cache:
        return project_cache[project_id]
    info = project_info(project_id)
    project_cache[project_id] = info
    return info

def add_version(version: dict, requested_by: str):
    version_id = version["id"]
    if version_id in version_cache:
        return
    project_id = version.get("project_id")
    # Some projects pin a dependency to a version ID whose compatibility
    # metadata is stale or incomplete. Prefer a current compatible release
    # from that same project before treating the dependency as unavailable.
    if not compatible(version):
        if project_id:
            resolve_project(project_id)
            replacement = choose_version(project_id)
            if compatible(replacement):
                print(
                    f"Dependency metadata fallback: {version.get('name', version_id)} "
                    f"{version.get('version_number', '')} -> "
                    f"{replacement.get('version_number', replacement['id'])}"
                )
                version = replacement
                version_id = version["id"]
                if version_id in version_cache:
                    return
            else:
                raise RuntimeError(
                    f"Required dependency {version.get('name', version_id)} "
                    f"has no compatible Forge {GAME_VERSION} release."
                )
        else:
            raise RuntimeError(
                f"Required dependency {version.get('name', version_id)} ({version_id}) "
                f"is not compatible with Forge {GAME_VERSION} and has no project metadata."
            )
    version_cache[version_id] = version
    if project_id:
        resolve_project(project_id)
    print(f"Resolved: {version.get('name', version_id)} {version.get('version_number', '')}")

    for dep in version.get("dependencies", []):
        if dep.get("dependency_type") != "required":
            continue
        if dep.get("version_id"):
            dep_version = request_json(f"{API}/version/{dep['version_id']}")
        elif dep.get("project_id"):
            resolve_project(dep["project_id"])
            dep_version = choose_version(dep["project_id"])
        else:
            continue
        add_version(dep_version, version.get("name", requested_by))

def main():
    for slug in PROJECTS:
        info = resolve_project(slug)
        chosen = choose_version(info["id"])
        add_version(chosen, slug)

    # Build a deterministic file list. Modrinth provides the direct download
    # URL and cryptographic hashes; no third-party mirrors are used.
    files = []
    seen_paths = set()
    for version in sorted(version_cache.values(), key=lambda v: (v.get("name", ""), v["id"])):
        project_slug = project_cache.get(version.get("project_id", ""), {}).get("slug", "")
        for file in version["files"]:
            if not file.get("primary"):
                continue
            hashes = file.get("hashes") or {}
            if not hashes.get("sha1") or not hashes.get("sha512"):
                raise RuntimeError(f"Missing SHA-1/SHA-512 for {file.get('filename')} ({version['id']})")
            filename = Path(file["filename"]).name
            relpath = f"mods/{filename}"
            if relpath in seen_paths:
                relpath = f"mods/{version['id']}-{filename}"
            seen_paths.add(relpath)
            env = {"client": "required", "server": "required"}
            if project_slug in CLIENT_ONLY:
                env = {"client": "required", "server": "unsupported"}
            elif project_slug in CLIENT_REQUIRED_SERVER_OPTIONAL:
                env = {"client": "required", "server": "optional"}
            files.append({
                "path": relpath,
                "hashes": {"sha1": hashes["sha1"], "sha512": hashes["sha512"]},
                "downloads": [file["url"]],
                "fileSize": file["size"],
                "env": env,
            })

    index = {
        "formatVersion": 1,
        "game": "minecraft",
        "versionId": PACK_VERSION,
        "name": PACK_NAME,
        "summary": "A balanced dragon adventure with festive winter decorations, snow behavior, building, QoL, performance and optional shaders.",
        "files": files,
        "dependencies": {
            "minecraft": GAME_VERSION,
            "forge": FORGE_VERSION,
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.writestr("modrinth.index.json", json.dumps(index, indent=2, sort_keys=True) + "\n")
        archive.writestr("overrides/README.txt", (
            "Dragonfire & Christmas — Minecraft 1.20.1 Forge\n\n"
            "Install this .mrpack with the Modrinth App. Java 17 is required.\n"
            "Shaders are optional: install a shader pack such as Complementary Reimagined "
            "or BSL after installing the pack. Oculus + Embeddium provide shader support.\n"
        ))
    with zipfile.ZipFile(OUT, "r") as archive:
        names = set(archive.namelist())
        assert "modrinth.index.json" in names
        loaded = json.loads(archive.read("modrinth.index.json"))
        assert loaded["dependencies"]["minecraft"] == GAME_VERSION
        assert len(loaded["files"]) == len(files)

    report = {
        "pack": PACK_NAME,
        "minecraft": GAME_VERSION,
        "forge": FORGE_VERSION,
        "file_count": len(files),
        "resolved_versions": [
            {"name": v.get("name"), "version": v.get("version_number"), "id": v["id"]}
            for v in sorted(version_cache.values(), key=lambda x: x.get("name", ""))
        ],
        "archive": str(OUT),
    }
    Path("dist/build-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nBuilt {OUT}")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"BUILD FAILED: {exc}", file=sys.stderr)
        sys.exit(1)

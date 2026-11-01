"""Validate release provenance and package the Python runtime SBOM assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


PROJECT_NAME = "vigil-spectra-32"
REPOSITORY_URL = "https://github.com/VIGIL-IoT/VIGIL-Spectra-32"
TAG_PATTERN = re.compile(r"^v(?P<version>\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?)$")
DEVELOPMENT_COMPONENTS = {"mypy", "pip-audit", "pip_audit", "pyright", "ruff"}


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package_release(
    *,
    tag: str,
    workflow_run: int,
    firmware_run: int,
    sbom_path: Path,
    output_dir: Path,
    uv_version: str,
) -> tuple[Path, Path, Path]:
    """Validate the tagged source and SBOM, then create release assets."""
    match = TAG_PATTERN.fullmatch(tag)
    if match is None:
        raise ValueError("tag must use vMAJOR.MINOR.PATCH SemVer format")
    if workflow_run < 1:
        raise ValueError("workflow run ID must be a positive integer")
    if firmware_run < 1:
        raise ValueError("firmware workflow run ID must be a positive integer")
    if not sbom_path.is_file():
        raise FileNotFoundError(f"SBOM file does not exist: {sbom_path}")

    tag_object_type = _git("cat-file", "-t", tag)
    if tag_object_type != "tag":
        raise ValueError(f"{tag} must be an annotated Git tag")

    source_commit = _git("rev-parse", f"{tag}^{{commit}}")
    pyproject_text = _git("show", f"{tag}:pyproject.toml")
    project = tomllib.loads(pyproject_text).get("project", {})
    project_name = project.get("name")
    project_version = project.get("version")
    if project_name != PROJECT_NAME:
        raise ValueError(f"tagged project name must be {PROJECT_NAME!r}")
    if project_version != match.group("version"):
        raise ValueError(
            f"tag {tag} does not match tagged pyproject version {project_version!r}"
        )

    sbom: dict[str, Any] = json.loads(sbom_path.read_text(encoding="utf-8"))
    if not isinstance(sbom, dict):
        raise ValueError("SBOM root must be a JSON object")
    if sbom.get("bomFormat") != "CycloneDX" or sbom.get("specVersion") != "1.5":
        raise ValueError("release SBOM must be CycloneDX 1.5")

    metadata = sbom.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError("SBOM metadata must be a JSON object")
    root_component = metadata.get("component")
    if not isinstance(root_component, dict):
        raise ValueError("SBOM metadata must include its project component")
    if root_component.get("name") != PROJECT_NAME:
        raise ValueError("SBOM project name does not match the tagged project")
    if root_component.get("version") != project_version:
        raise ValueError("SBOM project version does not match the release tag")

    components = sbom.get("components")
    if not isinstance(components, list) or not components:
        raise ValueError("runtime SBOM must contain at least one component")
    if any(not isinstance(component, dict) for component in components):
        raise ValueError("each SBOM component must be a JSON object")
    component_names = {str(component.get("name", "")).casefold() for component in components}
    leaked_development_tools = component_names & DEVELOPMENT_COMPONENTS
    if leaked_development_tools:
        names = ", ".join(sorted(leaked_development_tools))
        raise ValueError(f"development tools found in runtime SBOM: {names}")

    output_dir.mkdir(parents=True, exist_ok=True)
    sbom_name = f"spectra32-{tag}-runtime.cdx.json"
    sbom_asset = output_dir / sbom_name
    manifest_asset = output_dir / "release-manifest.json"
    checksum_asset = output_dir / "SHA256SUMS.txt"
    if any(path.exists() for path in (sbom_asset, manifest_asset, checksum_asset)):
        raise FileExistsError("release output already contains one or more asset names")

    shutil.copyfile(sbom_path, sbom_asset)
    sbom_digest = _sha256(sbom_asset)
    manifest = {
        "schema": "vigil-iot.release-manifest.v1",
        "repository": REPOSITORY_URL,
        "tag": tag,
        "version": project_version,
        "source_commit": source_commit,
        "uv_version": uv_version,
        "python_quality_run_id": workflow_run,
        "python_quality_run_url": f"{REPOSITORY_URL}/actions/runs/{workflow_run}",
        "firmware_build_run_id": firmware_run,
        "firmware_build_run_url": f"{REPOSITORY_URL}/actions/runs/{firmware_run}",
        "firmware_target": "classic esp32",
        "esp_idf_version": "6.1.0",
        "runtime_sbom": {
            "format": "CycloneDX",
            "spec_version": "1.5",
            "file": sbom_name,
            "sha256": sbom_digest,
            "component_count": len(components),
        },
        "generated_at_utc": datetime.now(UTC).isoformat(),
    }
    manifest_asset.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest_digest = _sha256(manifest_asset)
    checksum_asset.write_text(
        f"{sbom_digest}  {sbom_name}\n{manifest_digest}  {manifest_asset.name}\n",
        encoding="utf-8",
    )
    return sbom_asset, checksum_asset, manifest_asset


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True, help="annotated release tag, e.g. v0.2.0")
    parser.add_argument("--workflow-run", type=int, required=True, help="successful Python quality run ID for this tag")
    parser.add_argument("--firmware-run", type=int, required=True, help="successful ESP-IDF build run ID for this tag")
    parser.add_argument("--sbom", type=Path, required=True, help="CycloneDX 1.5 runtime SBOM from that workflow run")
    parser.add_argument("--output-dir", type=Path, required=True, help="empty or new directory for release assets")
    parser.add_argument("--uv-version", default="0.13.6", help="uv version used by the verified workflow")
    args = parser.parse_args()

    try:
        assets = package_release(
            tag=args.tag,
            workflow_run=args.workflow_run,
            firmware_run=args.firmware_run,
            sbom_path=args.sbom,
            output_dir=args.output_dir,
            uv_version=args.uv_version,
        )
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))

    for asset in assets:
        print(asset.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

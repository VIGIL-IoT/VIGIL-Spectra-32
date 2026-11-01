"""Tests for version-bound release asset packaging."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.package_release import package_release


class PackageReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.sbom_path = self.root / "runtime.cdx.json"
        self.firmware_lock_path = self.root / "dependencies.lock"
        self.output_dir = self.root / "release-assets"
        self._write_sbom()
        self._write_firmware_lock()

    def test_packages_version_matched_assets_and_provenance(self) -> None:
        with patch(
            "tools.package_release._git",
            side_effect=[
                "tag",
                "abcdef0123456789",
                '[project]\nname = "vigil-spectra-32"\nversion = "0.2.1"\n',
                self.firmware_lock_path.read_text(encoding="utf-8").strip(),
            ],
        ):
            sbom_asset, firmware_lock_asset, checksum_asset, manifest_asset = package_release(
                tag="v0.2.1",
                workflow_run=12345,
                firmware_run=67890,
                sbom_path=self.sbom_path,
                firmware_lock_path=self.firmware_lock_path,
                output_dir=self.output_dir,
                uv_version="0.13.6",
            )

        expected_sbom_name = "spectra32-v0.2.1-runtime.cdx.json"
        expected_lock_name = "spectra32-v0.2.1-esp-idf-dependencies.lock"
        self.assertEqual(sbom_asset.name, expected_sbom_name)
        self.assertEqual(sbom_asset.read_bytes(), self.sbom_path.read_bytes())
        self.assertEqual(firmware_lock_asset.name, expected_lock_name)
        self.assertEqual(
            firmware_lock_asset.read_bytes(), self.firmware_lock_path.read_bytes()
        )

        manifest = json.loads(manifest_asset.read_text(encoding="utf-8"))
        self.assertEqual(manifest["tag"], "v0.2.1")
        self.assertEqual(manifest["source_commit"], "abcdef0123456789")
        self.assertEqual(manifest["python_quality_run_id"], 12345)
        self.assertEqual(manifest["firmware_build_run_id"], 67890)
        self.assertEqual(manifest["runtime_sbom"]["component_count"], 1)
        self.assertEqual(
            manifest["firmware_dependency_inventory"]["file"], expected_lock_name
        )
        self.assertEqual(
            manifest["firmware_dependency_inventory"]["sha256"],
            hashlib.sha256(firmware_lock_asset.read_bytes()).hexdigest(),
        )
        self.assertIn(
            "excludes ESP-IDF built-in components",
            manifest["firmware_dependency_inventory"]["coverage"],
        )

        checksum_lines = checksum_asset.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(checksum_lines), 3)
        self.assertEqual(
            checksum_lines[0],
            f"{hashlib.sha256(sbom_asset.read_bytes()).hexdigest()}  {expected_sbom_name}",
        )
        self.assertEqual(
            checksum_lines[1],
            f"{hashlib.sha256(firmware_lock_asset.read_bytes()).hexdigest()}  {expected_lock_name}",
        )
        self.assertEqual(
            checksum_lines[2],
            f"{hashlib.sha256(manifest_asset.read_bytes()).hexdigest()}  release-manifest.json",
        )

    def test_rejects_lock_for_a_different_firmware_target(self) -> None:
        self.firmware_lock_path.write_text(
            "dependencies: {}\ntarget: esp32s3\n", encoding="utf-8"
        )
        with patch(
            "tools.package_release._git",
            side_effect=[
                "tag",
                "abcdef0123456789",
                '[project]\nname = "vigil-spectra-32"\nversion = "0.2.1"\n',
                self.firmware_lock_contents.strip(),
            ],
        ):
            with self.assertRaisesRegex(ValueError, "does not match the tagged source"):
                package_release(
                    tag="v0.2.1",
                    workflow_run=12345,
                    firmware_run=67890,
                    sbom_path=self.sbom_path,
                    firmware_lock_path=self.firmware_lock_path,
                    output_dir=self.output_dir,
                    uv_version="0.13.6",
                )

        self.assertFalse(self.output_dir.exists())

    def test_rejects_project_version_that_does_not_match_tag(self) -> None:
        with patch(
            "tools.package_release._git",
            side_effect=[
                "tag",
                "abcdef0123456789",
                '[project]\nname = "vigil-spectra-32"\nversion = "0.1.0"\n',
            ],
        ):
            with self.assertRaisesRegex(ValueError, "does not match"):
                package_release(
                    tag="v0.2.1",
                    workflow_run=12345,
                    firmware_run=67890,
                    sbom_path=self.sbom_path,
                    firmware_lock_path=self.firmware_lock_path,
                    output_dir=self.output_dir,
                    uv_version="0.13.6",
                )

        self.assertFalse(self.output_dir.exists())

    def test_rejects_development_dependency_in_runtime_sbom(self) -> None:
        self._write_sbom(component_names=["pandas", "ruff"])
        with patch(
            "tools.package_release._git",
            side_effect=[
                "tag",
                "abcdef0123456789",
                '[project]\nname = "vigil-spectra-32"\nversion = "0.2.1"\n',
                self.firmware_lock_contents.strip(),
            ],
        ):
            with self.assertRaisesRegex(ValueError, "development tools"):
                package_release(
                    tag="v0.2.1",
                    workflow_run=12345,
                    firmware_run=67890,
                    sbom_path=self.sbom_path,
                    firmware_lock_path=self.firmware_lock_path,
                    output_dir=self.output_dir,
                    uv_version="0.13.6",
                )

        self.assertFalse(self.output_dir.exists())

    def _write_sbom(self, component_names: list[str] | None = None) -> None:
        names = component_names or ["pandas"]
        sbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "metadata": {
                "component": {"name": "vigil-spectra-32", "version": "0.2.1"}
            },
            "components": [{"name": name} for name in names],
        }
        self.sbom_path.write_text(json.dumps(sbom), encoding="utf-8")

    def _write_firmware_lock(self) -> None:
        lock = """dependencies:
  espressif/mqtt:
    version: 1.1.0
  idf:
    source:
      type: idf
    version: 6.1.0
target: esp32
"""
        self.firmware_lock_contents = lock
        self.firmware_lock_path.write_text(lock, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

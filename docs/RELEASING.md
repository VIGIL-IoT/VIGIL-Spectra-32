# Release Process

GitHub Releases are published manually after the source tag has passed CI. No workflow creates a release or publishes a package automatically.

## Version policy

The project version in `pyproject.toml`, the `CITATION.cff` version, the annotated Git tag, the GitHub Release title, and the release manifest must agree. Use `vMAJOR.MINOR.PATCH` tags. While the project remains below 1.0, a new user-facing capability normally increments the minor version; a compatible correction increments the patch version.

The first two release milestones are:

| Version | Source snapshot | Scope |
|---|---|---|
| `v0.1.0` | `58ba1f7861b7fea6c8be2d529720f4f9584f9c7c` | Research-grade software-model baseline, repository CI, and runtime SBOM |
| `v0.2.0` | The release-preparation commit on `main` | Dashboard chart and brand refinements, plus broker-verified loopback MQTT coverage |

The next feature release should be `v0.3.0`, unless its scope is only a fix to `v0.2.0`.

## Release checklist

1. Update `pyproject.toml`, regenerate `uv.lock` with the pinned uv version, update `CITATION.cff`, and write the release entry under `docs/releases/` and `CHANGELOG.md`.
2. Push the release-preparation commit to `main`. Wait for all Python quality matrix jobs and MQTT integration checks to pass. If firmware source changes, also wait for the ESP-IDF build.
3. Create and push an annotated tag on that exact commit. Do not create the GitHub Release yet.
4. Run `python-quality.yml` against the tag and wait for it to pass. Run `esp32-firmware.yml` against the tag when firmware is included or changed.
5. Download the runtime SBOM artifact from that exact Python workflow run. Use `tools/package_release.py` to check the tag/version and SBOM, then create a checksum and a manifest containing the tag, commit, CI run ID, and SBOM digest.
6. Create the GitHub Release with the release note and all three assets: CycloneDX SBOM, checksum file, and source manifest. Attach assets before publishing so an immutable release never requires a later asset update.
7. Verify the published release points to the intended tag and contains the expected assets; download and check the SBOM digest.

Example PowerShell commands after the tag-specific workflow has passed:

```powershell
$tag = "v0.3.0"
$runId = "<successful-python-quality-run-id>"
$firmwareRunId = "<successful-esp-idf-build-run-id>"
$releaseDir = Join-Path $env:TEMP "spectra32-release-$tag"
gh run download $runId --name spectra32-python-runtime-sbom --dir $releaseDir
python tools/package_release.py --tag $tag --workflow-run $runId --firmware-run $firmwareRunId --sbom (Join-Path $releaseDir "spectra32-runtime.cdx.json") --output-dir $releaseDir
gh release create $tag --verify-tag --title "SPECTRA-32 $tag" --notes-file "docs/releases/$tag.md" (Join-Path $releaseDir "spectra32-$tag-runtime.cdx.json") (Join-Path $releaseDir "SHA256SUMS.txt") (Join-Path $releaseDir "release-manifest.json")
gh release view $tag
```

The runtime SBOM does not describe the ESP-IDF firmware dependency graph. Firmware build evidence and `firmware/vulnerable/basic-node/dependencies.lock` remain separate release references. Do not label the software SBOM as a complete hardware or firmware SBOM.

## Release notes

- [v0.1.0](releases/v0.1.0.md)
- [v0.2.0](releases/v0.2.0.md)

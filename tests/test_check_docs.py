"""Regression checks for repository documentation contracts."""

from __future__ import annotations

import unittest

from tools.check_docs import ROOT, check_markdown_targets, text_policy_errors


class DocumentationPolicyTests(unittest.TestCase):
    def test_rejects_unicode_and_encoded_em_dash(self) -> None:
        dash = chr(0x2014)
        source = (
            "literal " + dash + " dash\n"
            "encoded &" + "mdash; dash\n"
            "decimal &" + "#8212; dash\n"
            "hex &" + "#x2014; dash\n"
        )
        errors = text_policy_errors("example.md", source)
        self.assertEqual(len(errors), 4)
        self.assertTrue(all("forbidden em dash" in error for error in errors))

    def test_rejects_windows_and_unix_user_paths(self) -> None:
        windows_path = "C:" + chr(92) + "Users" + chr(92) + "person" + chr(92) + "repo"
        unix_path = "/" + "home" + "/" + "person" + "/repo"
        errors = text_policy_errors("example.txt", windows_path + "\n" + unix_path)
        self.assertEqual(len(errors), 2)
        self.assertTrue(all("personal machine path" in error for error in errors))

    def test_accepts_general_repository_guidance(self) -> None:
        source = "Use the repository root and a relative path such as docs/example.md.\n"
        self.assertEqual(text_policy_errors("example.md", source), [])

    def test_markdown_checker_covers_images_and_reference_definitions(self) -> None:
        markdown = ROOT / "docs" / "hardware-references.md"
        source = "![board](missing.svg)\n\n[details]: missing.md\n"
        errors = check_markdown_targets(markdown, source)
        self.assertEqual(len(errors), 2)
        self.assertTrue(all("missing link target" in error for error in errors))

    def test_markdown_checker_accepts_existing_image_and_reference_targets(self) -> None:
        markdown = ROOT / "docs" / "hardware-references.md"
        source = "![style](../assets/app.css)\n\n[readme]: ../README.md\n"
        self.assertEqual(check_markdown_targets(markdown, source), [])


if __name__ == "__main__":
    unittest.main()

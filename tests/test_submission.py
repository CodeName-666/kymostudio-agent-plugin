# SPDX-License-Identifier: GPL-3.0-only
"""Catch concrete directory-package regressions without claiming portal approval."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('check_submission', ROOT / 'tools/check_submission.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class SubmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.plugin = Path(self.temp.name) / 'plugin'
        shutil.copytree(ROOT / 'plugins/kymostudio', self.plugin)

    def change_interfaces(self, **values):
        for relative in ('plugin.json', '.codex-plugin/plugin.json'):
            path = self.plugin / relative
            data = json.loads(path.read_text(encoding='utf-8'))
            interface = data['interface'] if relative.startswith('.') else data['extensions']['com.openai']['interface']
            interface.update(values)
            path.write_text(json.dumps(data), encoding='utf-8')

    def test_clean_package_passes_without_claiming_review(self):
        report = checker.validate(self.plugin)
        self.assertEqual(report['format_checks'], 'passed')
        self.assertEqual(report['bundled_mcp_servers'], 0)
        self.assertEqual(report['provider_review'], 'not_performed')
        self.assertEqual(report['local_application_eligibility'], 'requires_provider_confirmation')

    def test_previously_oversized_subtitle_rejected(self):
        self.change_interfaces(shortDescription='Messquellen, Diagramme und Traces lokal steuern')
        with self.assertRaisesRegex(ValueError, 'shortDescription'):
            checker.validate(self.plugin)

    def test_missing_codex_publisher_rejected(self):
        path = self.plugin / '.codex-plugin/plugin.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        del data['author']
        path.write_text(json.dumps(data), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'author.name'):
            checker.validate(self.plugin)

    def test_missing_listing_category_or_capabilities_rejected(self):
        self.change_interfaces(category='')
        with self.assertRaisesRegex(ValueError, 'category'):
            checker.validate(self.plugin)
        self.change_interfaces(category='Developer Tools', capabilities=None)
        with self.assertRaisesRegex(ValueError, 'capability'):
            checker.validate(self.plugin)

    def test_unbundled_and_escaping_icons_rejected(self):
        for icon in ('./assets/missing.svg', '../outside.svg', '/absolute.svg'):
            with self.subTest(icon=icon):
                self.change_interfaces(logo=icon)
                with self.assertRaisesRegex(ValueError, 'logo'):
                    checker.validate(self.plugin)

    def test_rectangular_icon_rejected(self):
        (self.plugin / 'assets/logo.svg').write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 32"/>', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'square'):
            checker.validate(self.plugin)

    def test_local_kit_or_hooks_are_not_submission_package(self):
        for relative in ('.mcp.json', 'mcp.json', '.app.json', 'hooks/hooks.json'):
            with self.subTest(relative=relative):
                path = self.plugin / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{}', encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'neutral skills package'):
                    checker.validate(self.plugin)
                path.unlink()

    def test_insecure_listing_url_rejected(self):
        for url in ('http://example.com/privacy', 'https://token:secret@example.com/privacy'):
            with self.subTest(url=url):
                self.change_interfaces(privacyPolicyURL=url)
                with self.assertRaisesRegex(ValueError, 'privacyPolicyURL'):
                    checker.validate(self.plugin)

    def test_source_metadata_exposes_external_application_dependency(self):
        data = json.loads((ROOT / 'docs/submission/submission.json').read_text(encoding='utf-8'))
        self.assertFalse(data['submitted'])
        self.assertTrue(data['package']['requires_external_local_mcp'])
        self.assertTrue(data['package']['requires_local_desktop'])
        self.assertFalse(data['openai']['local_support_confirmed'])
        self.assertIsNone(data['package']['reviewer_app_download_url'])
        self.assertEqual(data['publisher']['contact_email'], 'kontakt@kymotrace.de')

    def test_no_rewriting_git_attributes_for_portal_archive(self):
        attributes = (ROOT / '.gitattributes').read_text(encoding='utf-8')
        self.assertFalse([line for line in attributes.splitlines()
                          if line.strip() and not line.startswith('#')])


if __name__ == '__main__':
    unittest.main()

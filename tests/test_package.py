# SPDX-License-Identifier: MIT
"""Verify distribution and client setup without application or extra dependencies."""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('package_plugin', ROOT / 'tools/package_plugin.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def test_public_archives_have_no_local_connection(self):
        output = builder.package(self.base / 'public')
        for archive_name in ('kymostudio-plugin.zip', 'kymostudio-agent-plugin.zip'):
            with self.subTest(archive=archive_name), zipfile.ZipFile(output / archive_name) as archive:
                names = archive.namelist()
                self.assertIn('LICENSE', names)
                self.assertTrue(any(name.endswith('/SKILL.md') for name in names))
                self.assertFalse(any(Path(name).name in
                    ('.mcp.json', 'mcp.json', 'mcp-client.json', 'codex-mcp.toml') for name in names))
                self.assertFalse(any(name.endswith('.zip') or '__pycache__' in name for name in names))
                for name in names:
                    text = archive.read(name).decode('utf-8')
                    self.assertNotIn(str(ROOT), text)
                    self.assertNotIn(str(self.base), text)
        with zipfile.ZipFile(output / 'kymostudio-agent-plugin.zip') as archive:
            for required in ('.agents/plugins/marketplace.json', '.claude-plugin/marketplace.json',
                             'tools/package_plugin.py', 'tests/test_package.py', 'docs/INSTALLATION.md'):
                self.assertIn(required, archive.namelist())

    def test_local_configuration_round_trip_and_secret_exclusion(self):
        adapter = self.base / 'Adapter mit Leerzeichen Ä.exe'
        adapter.write_bytes(uuid.uuid4().bytes)
        token = self.base / 'credentials.token'
        token.write_text(uuid.uuid4().hex, encoding='utf-8')
        server = builder.server_config('http://127.0.0.1:8766/mcp', adapter, token)
        output = builder.package(self.base / 'local', server)
        toml = tomllib.loads((output / 'codex-mcp.toml').read_text(encoding='utf-8'))
        self.assertEqual(toml['mcp_servers']['kymostudio']['command'], str(adapter.resolve()))
        self.assertEqual(toml['mcp_servers']['kymostudio']['args'], server['args'])
        for relative in ('mcp-client.json', 'plugins/kymostudio/.mcp.json'):
            data = json.loads((output / relative).read_text(encoding='utf-8'))
            self.assertEqual(data['mcpServers']['kymostudio'], server)
        portable = json.loads((output / 'plugins/kymostudio/mcp.json').read_text(encoding='utf-8'))
        self.assertEqual(portable['mcpServers']['kymostudio'], {'type': 'stdio', **server})
        overlay = json.loads((output / 'plugins/kymostudio/.codex-plugin/plugin.json').read_text(encoding='utf-8'))
        self.assertEqual(overlay['mcpServers'], './.mcp.json')
        for path in ('.agents/plugins/marketplace.json', '.claude-plugin/marketplace.json'):
            self.assertEqual(json.loads((output / path).read_text(encoding='utf-8'))['name'], 'kymostudio-local')
        with zipfile.ZipFile(output / 'kymostudio-agent-plugin.zip') as archive:
            combined = b'\n'.join(archive.read(name) for name in archive.namelist())
            self.assertNotIn(token.read_bytes(), combined)
            self.assertNotIn(adapter.read_bytes(), combined)

    def test_token_file_is_not_read_or_required_to_exist(self):
        adapter = self.base / 'adapter'
        adapter.touch()
        missing = self.base / 'not-created.token'
        result = builder.server_config('http://localhost:8766/mcp', adapter, missing)
        self.assertEqual(result['args'][-1], str(missing.resolve()))
        self.assertFalse(missing.exists())

    def test_endpoint_rejects_remote_or_ambiguous_configuration(self):
        adapter = self.base / 'adapter'
        adapter.touch()
        for endpoint in ('https://127.0.0.1:8766/mcp', 'http://example.com:8766/mcp',
                         'http://0.0.0.0:8766/mcp', 'http://127.0.0.1/mcp',
                         'http://127.0.0.1:0/mcp', 'http://127.0.0.1:99999/mcp',
                         'http://user:secret@localhost:8766/mcp', 'http://localhost:8766/other',
                         'http://localhost:8766/mcp?token=secret', 'http://localhost:8766/mcp#frag'):
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                builder.server_config(endpoint, adapter)

    def test_loopback_hosts_supported(self):
        adapter = self.base / 'adapter'
        adapter.touch()
        for endpoint in ('http://127.0.0.1:8766/mcp', 'http://localhost:8766/mcp',
                         'http://[::1]:8766/mcp'):
            with self.subTest(endpoint=endpoint):
                self.assertEqual(builder.server_config(endpoint, adapter)['args'], ['--endpoint', endpoint])

    def test_missing_adapter_rejected(self):
        with self.assertRaises(ValueError):
            builder.server_config('http://localhost:8766/mcp', self.base / 'missing')

    def test_existing_output_preserved(self):
        output = self.base / 'existing'
        output.mkdir()
        sentinel = output / 'keep.txt'
        sentinel.write_text('keep', encoding='utf-8')
        with self.assertRaises(FileExistsError):
            builder.package(output)
        self.assertEqual(list(output.iterdir()), [sentinel])
        self.assertEqual(sentinel.read_text(encoding='utf-8'), 'keep')

    def test_cli_from_unrelated_directory(self):
        output = self.base / 'cli'
        result = subprocess.run([sys.executable, str(ROOT / 'tools/package_plugin.py'),
                                 '--output', str(output)], cwd=self.base, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['mode'], 'portable')
        self.assertTrue((output / 'kymostudio-plugin.zip').is_file())

    def test_extracted_public_kit_can_repackage_without_app(self):
        original = builder.package(self.base / 'original')
        relocated = self.base / 'relocated'
        with zipfile.ZipFile(original / 'kymostudio-agent-plugin.zip') as archive:
            archive.extractall(relocated)
        result = subprocess.run([sys.executable, str(relocated / 'tools/package_plugin.py'),
                                 '--output', str(self.base / 'rebuilt')], cwd=self.base,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.base / 'rebuilt/kymostudio-agent-plugin.zip').is_file())

    def test_token_option_requires_local_adapter(self):
        output = self.base / 'rejected'
        result = subprocess.run([sys.executable, str(ROOT / 'tools/package_plugin.py'),
                                 '--output', str(output), '--token-file', 'private.token'],
                                cwd=self.base, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(output.exists())

    def test_local_kit_cannot_be_republished_as_portable(self):
        adapter = self.base / 'adapter'
        adapter.touch()
        local = builder.package(self.base / 'local',
                                builder.server_config('http://localhost:8766/mcp', adapter))
        output = self.base / 'unsafe-public'
        result = subprocess.run([sys.executable, str(local / 'tools/package_plugin.py'),
                                 '--output', str(output)], cwd=self.base,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(output.exists())


class RepositoryTests(unittest.TestCase):
    def test_manifests_and_marketplace_paths_agree(self):
        manifests = [json.loads((ROOT / 'plugins/kymostudio' / name).read_text(encoding='utf-8'))
                     for name in ('plugin.json', '.codex-plugin/plugin.json', '.claude-plugin/plugin.json')]
        self.assertEqual({item['name'] for item in manifests}, {'kymostudio'})
        self.assertEqual(len({item['version'] for item in manifests}), 1)
        self.assertEqual({item['license'] for item in manifests}, {'MIT'})
        for path in ('.agents/plugins/marketplace.json', '.claude-plugin/marketplace.json'):
            data = json.loads((ROOT / path).read_text(encoding='utf-8'))
            self.assertEqual(data['name'], 'kymostudio-agent-plugin')
            for entry in data['plugins']:
                source = entry['source']
                relative = source['path'] if isinstance(source, dict) else source
                target = (ROOT / relative).resolve()
                self.assertTrue(target.is_relative_to(ROOT))
                self.assertTrue((target / '.claude-plugin/plugin.json').is_file())
                if 'version' in entry:
                    self.assertEqual(entry['version'], manifests[0]['version'])

    def test_skill_references_are_in_package(self):
        plugin = ROOT / 'plugins/kymostudio'
        for document in plugin.rglob('*.md'):
            for link in re.findall(r'\]\(([^)]+)\)', document.read_text(encoding='utf-8')):
                if '://' in link or link.startswith('#'):
                    continue
                target = (document.parent / link.split('#')[0]).resolve()
                self.assertTrue(target.is_relative_to(plugin), link)
                self.assertTrue(target.is_file(), link)

    def test_no_personal_machine_paths_in_public_sources(self):
        # Construct forbidden literals rather than publishing those same paths here.
        fragments = ('No' + 'Name', 'D:' + '\\Projekte', 'build-' + 'backups')
        paths = [ROOT / 'README.md', *list((ROOT / 'docs').rglob('*.md')),
                 *list((ROOT / 'plugins').rglob('*'))]
        for path in paths:
            if path.is_file():
                content = path.read_text(encoding='utf-8')
                for fragment in fragments:
                    self.assertNotIn(fragment, content, str(path.relative_to(ROOT)))


if __name__ == '__main__':
    unittest.main()

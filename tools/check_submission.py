# SPDX-License-Identifier: MIT
"""Check published package constraints; provider eligibility/review remains separate."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlparse
import xml.etree.ElementTree as ET


def validate(plugin):
    plugin = Path(plugin).resolve()
    portable = json.loads((plugin / 'plugin.json').read_text(encoding='utf-8'))
    codex = json.loads((plugin / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
    claude = json.loads((plugin / '.claude-plugin/plugin.json').read_text(encoding='utf-8'))
    manifests = (portable, codex, claude)
    for manifest in manifests:
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', manifest['name']) or len(manifest['name']) > 64:
            raise ValueError('Invalid public plugin identifier')
        if not manifest.get('author', {}).get('name'):
            raise ValueError('Publisher author.name is required')
        if not re.fullmatch(r'\d+\.\d+\.\d+', manifest['version']):
            raise ValueError('Use an explicit release version')
    if len({(m['name'], m['version']) for m in manifests}) != 1:
        raise ValueError('Provider names and versions differ')
    interface = portable['extensions']['com.openai']['interface']
    if interface != codex['interface']:
        raise ValueError('Portable and Codex listing metadata differ')
    for key, limit in (('displayName', 30), ('shortDescription', 30),
                       ('longDescription', 4000), ('developerName', 80)):
        if not isinstance(interface.get(key), str) or not 0 < len(interface[key]) <= limit:
            raise ValueError(f'{key} must contain 1–{limit} characters')
    if not isinstance(interface.get('category'), str) or not interface['category']:
        raise ValueError('Listing category is required; confirm the portal category')
    capabilities = interface.get('capabilities')
    if not isinstance(capabilities, list) or len(capabilities) > 20 or any(
            not isinstance(item, str) or not 0 < len(item) <= 120 for item in capabilities):
        raise ValueError('Codex capability labels are required and must meet the listing budget')
    prompts = interface.get('defaultPrompt', [])
    if not isinstance(prompts, list) or len(prompts) > 3 or any(
            not isinstance(prompt, str) or not 0 < len(prompt) <= 128 for prompt in prompts):
        raise ValueError('Use at most three prompts of 1–128 characters')
    for key in ('websiteURL', 'supportURL', 'privacyPolicyURL', 'termsOfServiceURL'):
        url = interface.get(key, '')
        parsed = urlparse(url)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or len(url) > 1024:
            raise ValueError(f'{key} must be a public HTTPS URL without credentials')
    for key in ('logo', 'composerIcon'):
        relative = interface.get(key, '')
        path = (plugin / relative).resolve()
        if not relative.startswith('./') or not path.is_relative_to(plugin) or not path.is_file():
            raise ValueError(f'{key} must reference an included plugin image')
        if path.stat().st_size > 5 * 1024 * 1024:
            raise ValueError('Icon exceeds the image budget')
        if path.suffix == '.svg':
            svg = ET.parse(path).getroot()
            dimensions = list(map(float, svg.get('viewBox', '').split()))
            if len(dimensions) != 4 or dimensions[2] != dimensions[3] or dimensions[2] < 48:
                raise ValueError('SVG icon needs a square viewBox of at least 48 pixels')
        else:
            raise ValueError('This package preflight expects the bundled SVG artwork')
    readme = (plugin / 'README.md').read_text(encoding='utf-8')
    prose = re.sub(r'```.*?```', '', readme, flags=re.S)
    if len(prose.split()) < 40 or not (plugin / 'LICENSE').is_file():
        raise ValueError('Plugin README and license must be included')
    for name in ('.mcp.json', 'mcp.json', '.app.json', 'hooks/hooks.json'):
        if (plugin / name).exists():
            raise ValueError('Check the neutral skills package, not a locally configured kit')
    declarations = (*manifests, portable['extensions']['com.openai'])
    if any(key in manifest for manifest in declarations for key in ('mcpServers', 'apps', 'hooks')):
        raise ValueError('The neutral submission package must not declare local runtime components')
    files = [path for path in plugin.rglob('*') if path.is_file()]
    if len(files) > 512 or any(path.is_symlink() for path in plugin.rglob('*')):
        raise ValueError('Plugin file layout needs provider review')
    for path in files:
        limit = 5 * 1024 * 1024 if path.suffix == '.svg' else 256 * 1024
        if path.stat().st_size > limit:
            raise ValueError(f'Plugin file exceeds inspection budget: {path.name}')
    return {'format_checks': 'passed', 'package_version': portable['version'],
            'bundled_mcp_servers': 0, 'files': len(files), 'provider_review': 'not_performed',
            'local_application_eligibility': 'requires_provider_confirmation'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plugin', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'plugins/kymostudio')
    args = parser.parse_args()
    try:
        report = validate(args.plugin)
    except (OSError, ValueError, KeyError, ET.ParseError) as exc:
        parser.exit(2, str(exc) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()

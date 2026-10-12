# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 Christof Seidel
"""Create a portable release or a recipient's local MCP client kit."""
import argparse
import json
from pathlib import Path
import shutil
from urllib.parse import urlparse
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def server_config(endpoint, adapter, token_file=None):
    parsed = urlparse(endpoint)
    if (parsed.scheme != 'http' or parsed.hostname not in ('127.0.0.1', 'localhost', '::1')
            or parsed.path != '/mcp' or parsed.username or parsed.password
            or parsed.query or parsed.fragment or not parsed.port):
        raise ValueError('Use the explicit loopback http://127.0.0.1:PORT/mcp endpoint')
    command = Path(adapter).expanduser().resolve()
    if not command.is_file():
        raise ValueError('The selected adapter is not an existing file')
    args = ['--endpoint', endpoint]
    if token_file:
        args += ['--token-file', str(Path(token_file).expanduser().resolve())]
    return {'command': str(command), 'args': args}


def package(output, server=None):
    if server is None and any((ROOT / 'plugins/kymostudio' / name).exists()
                              for name in ('.mcp.json', 'mcp.json')):
        raise ValueError('Build public releases from the clean repository, not a configured local kit')
    output = Path(output).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=False)
    plugin = output / 'plugins/kymostudio'
    shutil.copytree(ROOT / 'plugins/kymostudio', plugin)
    shutil.copytree(ROOT / 'docs', output / 'docs')
    for directory in ('tools', 'tests'):
        shutil.copytree(ROOT / directory, output / directory,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for name in ('README.md', 'LICENSE', '.gitignore', '.gitattributes'):
        shutil.copyfile(ROOT / name, output / name)
    def write_json(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for relative in ('.agents/plugins/marketplace.json', '.claude-plugin/marketplace.json'):
        data = json.loads((ROOT / relative).read_text(encoding='utf-8'))
        if server:
            data['name'] = 'kymostudio-local'
        write_json(output / relative, data)
    if server:
        servers = {'mcpServers': {'kymostudio': server}}
        write_json(output / 'mcp-client.json', servers)
        write_json(plugin / '.mcp.json', servers)
        write_json(plugin / 'mcp.json', {
            '$schema': 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json',
            'mcpServers': {'kymostudio': {'type': 'stdio', **server}}})
        overlay_path = plugin / '.codex-plugin/plugin.json'
        overlay = json.loads(overlay_path.read_text(encoding='utf-8'))
        overlay['mcpServers'] = './.mcp.json'
        write_json(overlay_path, overlay)
        lines = ['[mcp_servers.kymostudio]', 'command = ' + json.dumps(server['command']),
                 'args = ' + json.dumps(server['args']),
                 'startup_timeout_sec = 20', 'tool_timeout_sec = 30']
        (output / 'codex-mcp.toml').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    plugin_zip, kit_zip = output / 'kymostudio-plugin.zip', output / 'kymostudio-agent-plugin.zip'
    with zipfile.ZipFile(plugin_zip, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(plugin.rglob('*')):
            if file.is_file():
                archive.write(file, file.relative_to(plugin).as_posix())
    with zipfile.ZipFile(kit_zip, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(output.rglob('*')):
            if file.is_file() and file not in (plugin_zip, kit_zip):
                archive.write(file, file.relative_to(output).as_posix())
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New output directory')
    parser.add_argument('--adapter', type=Path, help='Optional installed adapter for a local, personal kit')
    parser.add_argument('--endpoint', default='http://127.0.0.1:8766/mcp')
    parser.add_argument('--token-file', type=Path, help='Credential path; content is never read')
    args = parser.parse_args()
    if args.token_file and not args.adapter:
        parser.error('--token-file requires --adapter; public releases contain no local connection')
    try:
        server = server_config(args.endpoint, args.adapter, args.token_file) if args.adapter else None
        output = package(args.output, server)
    except (OSError, ValueError) as exc:
        parser.exit(2, str(exc) + '\n')
    print(json.dumps({'output': str(output), 'mode': 'local' if server else 'portable'}))


if __name__ == '__main__':
    main()

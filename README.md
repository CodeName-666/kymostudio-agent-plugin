# KymoStudio Agent Plugin

[![Tests](https://github.com/CodeName-666/kymostudio-agent-plugin/actions/workflows/tests.yml/badge.svg)](https://github.com/CodeName-666/kymostudio-agent-plugin/actions/workflows/tests.yml)

Use **Claude Code** or **Codex** to operate an existing local KymoStudio desktop:
measurement sources, charts, workspaces, trace capture/replay, and exports.

One shared `kymostudio-mcp` skill teaches the client to preserve acquisition
priority, respect BUSY limits, wait for completed jobs and capture publication,
and distinguish retained data from an entire measurement run.

## Requirements

- A KymoStudio build with local MCP support and its `KymoStudioMcp` stdio adapter.
- Claude Code or a local Codex client with plugin/MCP support.
- Python 3.11+ only for the optional configuration/package helper and tests.

The desktop application supplies the MCP server. This repository supplies the
operating skill, plugin manifests, marketplaces and setup helper. Install KymoStudio
separately and enable **Darstellung & Leistung → MCP-Steuerung**.

## Install the plugin

**Claude Code**:

```sh
claude plugin marketplace add CodeName-666/kymostudio-agent-plugin
claude plugin install kymostudio@kymostudio-agent-plugin
```

**Codex**:

```sh
codex plugin marketplace add CodeName-666/kymostudio-agent-plugin
codex plugin add kymostudio@kymostudio-agent-plugin
```

The GitHub plugin contains no machine-specific MCP command. Configure the
connection once using the adapter installed on your computer:

```sh
claude mcp add --transport stdio --scope user kymostudio -- "<ADAPTER_PATH>" --endpoint http://127.0.0.1:8766/mcp
codex mcp add kymostudio -- "<ADAPTER_PATH>" --endpoint http://127.0.0.1:8766/mcp
```

Replace `<ADAPTER_PATH>` with the actual `KymoStudioMcp.exe` executable on Windows
or your executable adapter on another platform. Use the endpoint displayed by
the app. For a custom credential location, append `--token-file "<TOKEN_FILE>"`.
The adapter reads the credential; do not paste the token into a chat or manifest.
Run only the command for the client you use. Restart its MCP connection/session.

## Use it

Claude Code:

```text
/kymostudio:kymostudio-mcp Prüfe meine Messquellen und den Capture-Zustand.
```

In Codex, select the installed **KymoStudio** skill, or use
`$kymostudio-mcp` when your host exposes the unqualified name. The displayed
plugin namespace can vary by host.

Start with `kymo_status` and `kymo_capabilities`. Verify the desktop `instance_id`
and GUI readiness. For example, ask to create a time-series chart for an existing
signal or export retained data to a granted folder.

## Generate local configuration or an offline kit

After cloning this repository:

```sh
python tools/package_plugin.py --adapter "<ADAPTER_PATH>" --endpoint http://127.0.0.1:8766/mcp --output local/client-kit
```

This creates Codex TOML, generic stdio JSON and an optional local plugin containing
your adapter configuration. It does not edit client settings, start the app,
or read token contents. The output directory must be new. Custom token paths
are supplied through `--token-file "<TOKEN_FILE>"`.

Local kits contain user-selected absolute paths and are intended for that
computer. They are ignored by Git. Public release archives are created without
`--adapter` and contain no machine-specific connection configuration.

[Deutsche Installationsanleitung](docs/INSTALLATION.md) ·
[Download releases](https://github.com/CodeName-666/kymostudio-agent-plugin/releases) ·
[Development and release](docs/DEVELOPMENT.md) ·
[Skill](plugins/kymostudio/skills/kymostudio-mcp/SKILL.md)

[Official directory submission preparation](docs/submission/README.md) documents
the candidate metadata, review scenarios and the required provider/account checks.
The local application prerequisite requires OpenAI eligibility confirmation.
Prepared files and successful local checks do not imply directory approval.

## Tests

No test dependencies are required:

```sh
python -m unittest discover -s tests -v
```

GitHub Actions runs these checks on Windows and Linux with Python 3.11 and 3.12.
Tests cover public archive portability, client configuration round-trips,
endpoint validation, credential exclusion and non-destructive output handling.
Provider CLI validation and a real desktop/adapter smoke check are documented
separately; unit tests do not certify physical measurement hardware.

## Scope and license

The published plugin is for local desktop clients. Its installation does not
publish the desktop server on the Internet or constitute a listing in either
vendor's official public plugin directory.

Plugin, helper and documentation: **GPL-3.0-only**, see [LICENSE](LICENSE).
KymoStudio's application/installer is distributed separately under its own terms.
This project is maintained by Christof Seidel and is not an official Anthropic
or OpenAI product.

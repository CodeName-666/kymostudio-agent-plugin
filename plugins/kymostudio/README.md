# KymoStudio

Shared operating skill for local Claude Code and Codex clients.

![KymoStudio logo](assets/logo.svg)

Install KymoStudio with MCP support, enable its local endpoint, then configure
the MCP client with your installed `KymoStudioMcp` adapter. This portable plugin
does not assume any installation path or contain a credential.

- Claude Code skill: `/kymostudio:kymostudio-mcp`
- Codex: select the KymoStudio skill; `$kymostudio-mcp` when available unqualified
- First tools: `kymo_status`, `kymo_capabilities`
- Respect acquisition/capture priority and wait for successful jobs before
  claiming a completed export or capture.

[Installation](https://github.com/CodeName-666/kymostudio-agent-plugin/blob/main/docs/INSTALLATION.md)
and [repository](https://github.com/CodeName-666/kymostudio-agent-plugin).

MIT; see `LICENSE`. The desktop application is distributed separately.

[Privacy and data handling](PRIVACY.md) · [Support](SUPPORT.md).
Maintainer: Christof Seidel, kontakt@kymotrace.de.

The plugin's useful workflows require local application access and a separate
MCP connection. Installing the instruction package alone does not make the
desktop reachable from a cloud-only conversation. Tool results returned to
your agent may be processed by its model provider. Queries and capture jobs
must follow the application's capability limits; the skill does not establish
an unconditional guarantee of lossless acquisition.

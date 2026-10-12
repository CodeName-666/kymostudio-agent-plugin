# KymoStudio

Shared operating skill for local Claude Code and Codex clients.

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

GPL-3.0-only; see `LICENSE`. The desktop application is distributed separately.

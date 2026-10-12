# Prepared provider inquiries

These drafts have not been sent. Sender: **Christof Seidel**,
**kontakt@kymotrace.de**. Use an existing provider contact or the route the
provider supplies; no recipient address or partner relationship is assumed.

## OpenAI: local application eligibility

**Subject:** Local KymoStudio operating skill — directory eligibility and review path

I maintain KymoStudio and the public agent package at
https://github.com/CodeName-666/kymostudio-agent-plugin.
The candidate is a shared operating skill for local Codex and Claude Code clients.
It guides measurement acquisition, charts, workspace changes, trace capture/replay
and exports through a separately installed KymoStudio MCP adapter.

The desktop server intentionally binds only to loopback. The public skill package
contains no server executable, endpoint credentials, fixed installation path,
lifecycle hooks or external app references. Its core workflow nevertheless needs
access to the user's running desktop application. A cloud-only host cannot reach
that instance without an additional supported connection architecture.

Your submission guide asks developers to contact OpenAI before submitting plugins
whose core value requires local execution, hardware or application access. Please
confirm the supported directory and review path for this package, including whether
a desktop-specific listing is available and how to declare the external local MCP
prerequisite. We will not represent it as a self-contained cloud skill or a public
remote MCP server.

The repository contains manifests, product artwork, privacy/data-flow disclosure,
installation instructions, passing distribution tests and proposed reviewer cases.
A previous generated stdio setup was smoke-tested against the packaged desktop:
43 tools, synthetic signal data and a confirmed source stop. Account identity,
reviewer application access and portal scans will be completed for the agreed path.

## Anthropic: official Claude Code marketplace

**Subject:** KymoStudio — local operating skill and official-marketplace review route

I maintain the KymoStudio agent package at
https://github.com/CodeName-666/kymostudio-agent-plugin,
plugin folder `plugins/kymostudio`, candidate version `0.1.1`.
It provides a shared operating skill with synthetic demo, capture, chart, workspace
and export workflows for a separately installed local KymoStudio MCP connection.

Claude Code accepts the plugin and marketplace with strict native validation.
The published GitHub version installs successfully in a disposable Claude Code
profile. Public packages contain no machine-specific connection or credential.
The README clearly explains the separately installed application and that tool
results can reach the model provider.

Your current Claude Code publishing documentation distinguishes the directory
portal from a listing in `claude-plugins-official`. Please confirm the current
route and prerequisite partner relationship, if any, for official-marketplace
consideration. We also need to confirm how a listing should describe a skill
whose useful actions require a separately configured local MCP connection.

Prepared materials include publisher/contact information, licensing, artwork,
privacy disclosure, installation steps and review scenarios. We can provide a
synthetic reviewer workspace once the application-access route is agreed.

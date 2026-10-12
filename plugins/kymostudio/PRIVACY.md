# Privacy and data handling

Publisher: Christof Seidel. Contact: kontakt@kymotrace.de.

This statement covers the KymoStudio agent plugin: static operating instructions,
manifests and artwork. It does not replace the policies of your model provider,
GitHub, the separately installed desktop application or your measurement sources.

## Data involved in a workflow

The plugin itself runs no background service, adds no telemetry and stores no
runtime personal data. Installation stores its static files in the client cache.

When you ask your agent to use the separately configured KymoStudio MCP server,
tool results can include signal names and values, timestamps, source descriptions,
workspace details and local file paths. Such data can contain personal information
depending on what you measure. The MCP connection uses the desktop's loopback
endpoint, but tool results become available to the agent client and its model
provider under that client's settings and policies. Local transport does not mean
that the model provider cannot receive returned measurement data.

The operating instructions require bounded queries, granted local file folders
and disclosure of buffer limits. They do not request credentials or upload data
to a publisher-operated service. The configured adapter reads its local token
file for authentication; token contents must not enter prompts or public packages.

## Retention and controls

The plugin retains no runtime measurement or personal data. Client conversations
and model-provider retention follow the selected client's policy. Desktop files,
exports and captures remain under your local application's configuration and your
deletion controls; this plugin sets no separate retention period for them.

You can disable MCP in KymoStudio, remove the client connection, restrict folder
grants, use the application's read-only mode, or uninstall the plugin. Disabling
MCP is separate from stopping measurement acquisition or deleting local files.

Use non-personal synthetic data for review and demonstrations. Remove credentials,
personal measurements and local user names before posting issue reports. Support
messages sent by email or through GitHub are separate from automated plugin data
flows and follow those services' handling; discuss deletion requests with the
publisher at the contact above.

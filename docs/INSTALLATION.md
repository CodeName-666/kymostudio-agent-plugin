# Installation für Claude Code und Codex

## 1. KymoStudio vorbereiten

Installiere eine KymoStudio-Version mit MCP-Unterstützung und starte sie.
Öffne **Darstellung & Leistung → MCP-Steuerung**, aktiviere den Zugriff und
übernimm Port, Lesemodus und freigegebene lokale Dateiordner.

Der Dialog zeigt den tatsächlichen Endpunkt und Token-Dateipfad. Für eine
dauerhafte Verbindung eignet sich ein fester Port, z. B. 8766. Mit Port 0 musst
du den tatsächlich vergebenen Port anschließend im Client verwenden.

Jede Desktop-Instanz benötigt einen eigenen Port. Der stdio-Adapter verbindet
sich mit der laufenden Anwendung; er startet keine zweite Messwerterfassung.

## 2. Plugin installieren

Claude Code:

```powershell
claude plugin marketplace add CodeName-666/kymostudio-agent-plugin
claude plugin install kymostudio@kymostudio-agent-plugin
```

Codex:

```powershell
codex plugin marketplace add CodeName-666/kymostudio-agent-plugin
codex plugin add kymostudio@kymostudio-agent-plugin
```

Der gemeinsame Marketplace heißt `kymostudio-agent-plugin`, das Plugin
`kymostudio`. Anschließend eine neue Unterhaltung öffnen oder den Client neu laden.

## 3. MCP-Verbindung einrichten

Wähle den auf deinem Rechner installierten Adapterpfad. In PowerShell:

```powershell
$adapterPath = '<ADAPTER_PATH>'
$endpoint = 'http://127.0.0.1:8766/mcp'
```

Ersetze den Platzhalter durch den tatsächlichen Pfad zu `KymoStudioMcp.exe`.
Übernimm für `$endpoint` den Wert aus KymoStudio.

Claude Code:

```powershell
claude mcp add --transport stdio --scope user kymostudio -- $adapterPath --endpoint $endpoint
claude mcp list
```

Codex:

```powershell
codex mcp add kymostudio -- $adapterPath --endpoint $endpoint
codex mcp list
```

Bei einem eigenen Credential-Dateipfad an den Registrierungsbefehl
`--token-file '<TOKEN_FILE>'` anhängen. Das Token selbst gehört weder in die
Konfiguration noch in den Chat. Der Adapter verwendet sonst den Standardpfad des
KymoStudio-Profils. Nach Tokenrotation die Adapterverbindung neu starten.

Plugin und MCP-Verbindung sind getrennte Voraussetzungen. Der veröffentlichte
Plugin-Stand enthält absichtlich keine voreingestellte Adapterinstallation.

## 4. Lokale Konfigurationsdateien erzeugen

Wenn du TOML/JSON statt der CLI nutzen möchtest, klone dieses Repository und
rufe aus dessen Wurzel den Standardbibliothek-Generator auf:

```powershell
python tools/package_plugin.py --adapter $adapterPath --endpoint $endpoint --output local/client-kit
```

Es entstehen:

- `codex-mcp.toml`: Abschnitt für die vorhandene Codex-Konfiguration;
- `mcp-client.json`: stdio-Konfiguration für entsprechende JSON-MCP-Hosts;
- `plugins/kymostudio`: lokales Plugin mit deiner konkreten MCP-Verbindung;
- beide Marketplace-Dateien, Anleitung und ZIP-Archive.

Der Generator verändert keine globalen Einstellungen und überschreibt keine
vorhandenen Ausgabeordner. Er liest keine Credential-Inhalte. Die erzeugten
Dateien können Adapter- und Token-Dateipfade enthalten; sie sind lokale
Einrichtungsergebnisse und gehören nicht ins öffentliche Repository.

Alternativ den erzeugten Ordner als lokalen Marketplace installieren. Dieser
heißt `kymostudio-local`. Für diese Variante den direkten MCP-Servereintrag nicht
zusätzlich aktivieren, wenn nur eine Verbindung zur Instanz benötigt wird.

## 5. Bedien-Skill aufrufen

Claude Code: `/kymostudio:kymostudio-mcp`.
Codex: installierten KymoStudio-Skill auswählen; bei unqualifiziertem Namen
`$kymostudio-mcp` verwenden. Plugin-Namensräume können je nach Host abweichen.

Eine persönliche Installation des Skill-Ordners ist ebenfalls möglich:
`~/.claude/skills/kymostudio-mcp` oder `~/.codex/skills/kymostudio-mcp`.
Claude verwendet dann `/kymostudio-mcp`.

Prüfe zuerst `kymo_status` und `kymo_capabilities`. Die `instance_id` muss zu deiner
Desktop-Instanz passen. Ein Auftrag kann etwa lauten:

> Prüfe meine Messquellen und erstelle für das vorhandene Temperatursignal ein Zeitdiagramm.

## Fehlerdiagnose

| Symptom | Prüfung |
|---|---|
| Verbindung verweigert | Läuft die App, ist MCP aktiv, stimmt der Port? |
| UNAUTHORIZED | Richtige Token-Datei, nach Rotation neu verbunden, Lesemodus passend? |
| PATH_DENIED | Liegt die Datei im tatsächlich freigegebenen lokalen Ordner? |
| BUSY | Aufnahme/Rückstand respektieren; begrenzt warten, keine Poll-Flut |
| NOT_READY | GUI, Verbindung oder Trace-Session noch nicht bereit |
| CONFLICT | Dateiexistenz bzw. aktuelle Workspace-Revision prüfen |

Während Capture nur die zugelassenen leichten Werkzeuge verwenden. Capture-Stop
liefert einen Job: erst nach `data.job.state == succeeded` ist die Datei bestätigt.
Danach analysieren oder exportieren. Ein begrenzter Rohpuffer enthält nicht
automatisch die gesamte Laufzeit einer Messung.

Offizielle Quellen:
[Claude Code MCP](https://code.claude.com/docs/en/mcp),
[Claude Plugins](https://code.claude.com/docs/en/plugins-reference),
[Codex MCP](https://developers.openai.com/codex/mcp/),
[Codex Plugins](https://developers.openai.com/plugins/build/plugins).

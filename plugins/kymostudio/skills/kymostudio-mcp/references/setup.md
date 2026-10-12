# Lokalen MCP-Client verbinden

1. KymoStudio starten und **Darstellung & Leistung → MCP-Steuerung** öffnen.
2. Zugriff aktivieren; Port, Lesemodus und lokale Import-/Exportordner einstellen
   und übernehmen. Für einen dauerhaften Client eignet sich ein fester Port.
3. Angezeigten Endpunkt und Token-Dateipfad verwenden. Bei Port 0 den tatsächlich
   gewählten Port übernehmen. Jede Instanz benötigt ihren eigenen Port.
4. Den installierten stdio-Adapter im Client registrieren. Die Anwendung muss
   bereits laufen. Der Adapter liest das Token; dessen Inhalt gehört nicht in Chats.

## Öffentliches Plugin installieren

Claude Code:

```sh
claude plugin marketplace add CodeName-666/kymostudio-agent-plugin
claude plugin install kymostudio@kymostudio-agent-plugin
```

Codex:

```sh
codex plugin marketplace add CodeName-666/kymostudio-agent-plugin
codex plugin add kymostudio@kymostudio-agent-plugin
```

Das öffentliche Plugin enthält den Skill und keine rechnerabhängige
Serverkonfiguration. `<ADAPTER_PATH>` durch den tatsächlichen Pfad zur installierten
`KymoStudioMcp.exe` bzw. zum ausführbaren Adapter ersetzen; den Beispiel-Endpunkt
durch die Anzeige der Anwendung ersetzen. Nur den passenden Client einrichten:

```sh
claude mcp add --transport stdio --scope user kymostudio -- "<ADAPTER_PATH>" --endpoint http://127.0.0.1:8766/mcp
codex mcp add kymostudio -- "<ADAPTER_PATH>" --endpoint http://127.0.0.1:8766/mcp
```

Bei einem abweichenden Token-Dateipfad `--token-file "<TOKEN_FILE>"` anhängen.
Keine Standardpfade erraten: Installationsordner und App-Dialog sind maßgeblich.

## Manuelle Konfiguration und lokale Pakete

Codex akzeptiert in seiner Benutzerkonfiguration folgenden Abschnitt:

```toml
[mcp_servers.kymostudio]
command = '<ADAPTER_PATH>'
args = ['--endpoint', 'http://127.0.0.1:8766/mcp']
startup_timeout_sec = 20
tool_timeout_sec = 30
```

Andere stdio-Hosts verwenden denselben Befehl und dieselben Argumente:

```json
{
  "mcpServers": {
    "kymostudio": {
      "command": "<ADAPTER_PATH>",
      "args": ["--endpoint", "http://127.0.0.1:8766/mcp"]
    }
  }
}
```

Der Paketgenerator im Repository erstellt diese Dateien und ein lokal
konfiguriertes Plugin. Solche Pakete enthalten die ausgewählten absoluten Pfade
und sind nur für diesen Rechner bestimmt. Beim lokalen Plugin den Marketplace
`kymostudio-local` verwenden und den Server nicht zusätzlich direkt registrieren.
Die [Installationsanleitung](https://github.com/CodeName-666/kymostudio-agent-plugin/blob/main/docs/INSTALLATION.md)
beschreibt alle Schritte.

## Zustand und Fehlerdiagnose

MCP-Verbindung bzw. Sitzung neu starten. Danach `kymo_status` und
`kymo_capabilities` aufrufen und die richtige `instance_id` prüfen. Bei Claude
Code lautet die Plugin-Invokation `/kymostudio:kymostudio-mcp`. Bei persönlicher
Skill-Installation lautet sie `/kymostudio-mcp`; Codex kann `$kymostudio-mcp`
oder einen vom Host angezeigten Plugin-Namensraum verwenden.

- Verweigert: Zugriff aktivieren, richtige Token-Datei und Lesemodus prüfen.
- Nicht erreichbar: laufende App, angezeigten Endpunkt und Portkonflikte prüfen.
- Nach Tokenrotation: Adapter/MCP-Verbindung neu starten.
- Keine Werkzeuge: Server im richtigen Host registrieren und Verbindung neu laden.
- `PATH_DENIED`: im App-Dialog echte lokale Ordner freigeben, nicht mit `..`
  oder Netzwerkpfaden umgehen.

Streamable HTTP verwendet `Authorization: Bearer <Token>`. Der stdio-Adapter
vermeidet die manuelle Übergabe und liest nach einem Neustart ein erneuertes Token.
Die App unterstützt feste lokale Token und keinen OAuth-Login; `codex mcp login`
ist dafür kein Einrichtungsschritt. Loopback erreicht ausschließlich die lokale
App. Dieses Plugin stellt keinen Cloud-Server bereit.

Quellen, geprüft 2026-10-12:
[Codex MCP](https://developers.openai.com/codex/mcp/),
[Codex Plugins](https://developers.openai.com/plugins/build/plugins),
[Claude Code MCP](https://code.claude.com/docs/en/mcp),
[Claude Plugin-Referenz](https://code.claude.com/docs/en/plugins-reference).

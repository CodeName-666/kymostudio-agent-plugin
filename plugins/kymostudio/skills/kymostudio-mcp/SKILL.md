---
name: kymostudio-mcp
description: "Konfiguriere lokale KymoStudio-MCP-Clients und bediene die laufende Desktop-Instanz: Messquellen, Diagramme, Workspace, Geräteparameter (Rückkanal), Messaufnahmen, Trace/Capture/Replay, Logs und Exporte. Verwende diesen Skill für die Bedienung und Diagnose über MCP, nicht für Änderungen an KymoStudios Quellcode."
---

# KymoStudio über MCP bedienen

KymoStudio ist die laufende Desktop-Anwendung und der lokale MCP-Server.
Codex oder Claude Code ist der MCP-Client. `KymoStudioMcp.exe` ist der stdio-Adapter zur selben
Desktop-Instanz; er startet keine zweite Messwerterfassung.

## Verbindung und Zustand

- Nutze die tatsächlich verfügbaren MCP-Werkzeuge mit Namen `kymo_*`; ihr
  Host-Präfix kann je nach Client oder Plugin variieren. Erfinde keine Toolnamen,
  Verbindungs-, Signal-, Chart- oder Session-IDs.
- Bei fehlenden Werkzeugen oder Verbindungsproblemen lies
  [references/setup.md](references/setup.md). Öffne einen eingerichteten
  KymoStudio-Server; wechsle nicht ungefragt Endpunkt oder Instanz.
- Beginne mit `kymo_status` und `kymo_capabilities`. Beachte `read_only`,
  `backend_ready`, `workspace_ready` und `instance_id`; Workspace-Werkzeuge
  benötigen die aufgebaute GUI. Prüfe bei mehreren Instanzen die Zuordnung.
- Antworten enthalten `schema_version`, `request_id` und `data` oder `error`.
  `data.instance_id` bezeichnet die Desktop-Instanz. Ein `is_error`-Ergebnis
  ist ein Fehler, auch wenn Textinhalt vorhanden ist.
- Änderungen sind unmittelbar in der GUI sichtbar. Bestehende Quellen und
  Diagramme bevorzugt weiterverwenden. Lege eine Testquelle nur für einen
  angeforderten Demo-/Prüfablauf an. Bestehende Autorisierung gilt weiter.

## Vorrang für Messwerterfassung und Capture

Logging meint primär vollständigen Messwerteingang, lückenlose Trace-Aufzeichnung
und vollständigen Capture-Abschluss. Textlogs sind ein zusätzlicher Prüfbereich.

- Lies `capture_allowed` und die Limits aus `kymo_capabilities`. Während Capture
  oder Speicherung laufen, nur dort zugelassene Operationen ausführen.
  Die Liste verwendet Operationsnamen ohne `kymo_`-Präfix. Historienanalysen,
  Diagrammänderungen und Exporte bis nach Capture verschieben.
- `BUSY` ist eine bewusste Zulassungsgrenze zum Schutz der Erfassung. Keine
  parallelen Poll-Schleifen oder wiederholten Großabfragen. Bei kurzem Rückstand
  höchstens drei Wiederholungen mit 0,1/0,25/0,5 s Pause; bleibt er bestehen,
  Zustand melden und abhängige Arbeit zurückstellen.
- Live-Werte sparsam abfragen, gewöhnlich 1–2 Mal/s. Das Serverlimit von 20
  Requests/s gilt pro Desktop-Protokollprozess für alle Clients zusammen.
- Eine angeforderte Trace-Aufzeichnung mit `kymo_capture_stop`, eine Messaufnahme
  mit `kymo_recording_stop` beenden und ihren Job
  bis zum tatsächlichen Abschluss verfolgen. Erst danach Quelle stoppen,
  analysieren oder exportieren. Aufnahme und Speicherung sind verschiedene Zustände.
  GUI und MCP können die Aufnahme des jeweils anderen Bedienwegs stoppen.
- Bestehende Aufnahme oder Quelle nicht allein für eine Analyseanfrage stoppen.
  Deaktivieren von MCP und Anzeigenpause stoppen die Messwerterfassung nicht.

## Arbeitsabläufe

- **Messen:** `kymo_connections` lesen; Typen/Settings über
  `kymo_connection_types`, bei seriellen Quellen Ports über `kymo_ports`
  entdecken. Angeforderte Quelle anlegen/konfigurieren, Startjob abwarten,
  `kymo_signals` und `kymo_values` lesen. `connected` ist noch kein Beleg für
  eingegangene Messwerte; Diagnostik und tatsächliche Signale prüfen.
- **Diagramme:** Chart erstellen, Renderer-Job abwarten, numerische Signale
  zuordnen. Typen: `time_series`, `xy_line`, `xy_scatter`, `xyz_scatter`,
  `runtime_trace`, `function_flow`, `measurement`. Trace-Charts verwenden eine Trace-Session,
  keine numerischen Assignments. Typabhängige View-Parameter verwenden.
- **Workspace:** `kymo_workspace_get` liefert Live-Zustand und Revision. Für
  vollständigen Ersatz frische `expected_revision` und `replace_existing: true`
  verwenden. Bei `CONFLICT` neu lesen und Änderungen abgleichen; einen fremden
  GUI-Stand nicht blind ersetzen. Import zuerst mit `preview: true`; tatsächlicher
  Import stoppt Quellen und löscht numerische Rohdaten, muss im Auftrag liegen.
- **Rohdaten:** `kymo_samples` liefert höchstens 1.000 Zeilen. Nur bei vorhandenem
  `next_cursor` mit demselben `snapshot_id` weiterblättern; eine vollständige
  Antwort hat `snapshot_id: null`. Snapshots laufen nach 60 s ab, höchstens zwei
  sind gleichzeitig gespeichert. Für Live-Signale beschreiben Statistik und CSV den
  begrenzten Rohpuffer, nicht automatisch die gesamte Laufzeit.
- **Messaufnahmen (ab KymoStudio 2.7):** `kymo_recordings` zeigt die laufende
  Aufnahme und die geöffneten. `kymo_recording_start` mit einem `.kymorec`-Pfad in
  einem freigegebenen Ordner nimmt alle verbundenen Capture-Quellen auf (keine
  Testquellen); `kymo_recording_stop` liefert einen Job, erst nach `succeeded` ist
  die Datei abgeschlossen. Eine laufende Aufnahme nur auf ausdrücklichen Wunsch
  stoppen. `kymo_recording_open` (Job) lädt eine Aufnahme mit eigenen Signal-IDs
  (`rec<n>-…`, Anzeigename mit „(Aufnahme)“); für diese Signale lesen `kymo_samples`
  und `kymo_statistics` die gesamte Aufnahme. `kymo_recording_close` mit dem
  `prefix` entlädt sie, die Datei bleibt. `kymo_recording_info` und
  `kymo_recording_export` (CSV, optional `start`/`end`) sind Jobs.
  `kymo_capture_*` betrifft ausschließlich Trace-Aufzeichnungen.
- **Diagnose:** `kymo_diagnostics` enthält Empfang, Verluste, Pufferfüllung, den
  Aufnahmezustand und unter `display` die Bildrate des Hauptfensters (`fps`,
  `max_gap_ms`); Diagramme rücken nur mit neuen Daten vor, langsame Quellen ergeben
  eine niedrige Rate. `kymo_logs` liest das Ende von `app`, `hang`
  (Hänger-Tracebacks), `mcp` oder `stderr`; Logs nur auszugsweise berichten.
- **Geräteparameter (ab KymoStudio 2.7):** Firmware mit KymoCore 7.1 meldet ihre
  Parameter (Name, Einheit, Grenzen); `kymo_parameters` liest sie samt Gerätewert
  und Schreibstatus, `kymo_parameters_request` fragt die Liste neu an. Werte nur
  schreiben, wenn der Auftrag es verlangt: Sie ändern sofort das Verhalten des
  realen Geräts (Regler, Antrieb, Heizung). `kymo_parameter_set` prüft die Grenzen
  vorab (`INVALID_ARGUMENT` bei Überschreitung) und liefert einen Job. Er gelingt
  (`succeeded`) nur, wenn das Gerät den Wert bestätigt. Sonst scheitert er mit
  `DEVICE_REJECTED` (Gerät behält einen anderen Wert) oder `DEVICE_NO_ANSWER`
  (keine Rückmeldung); auch dann steht die Parameterzeile mit Gerätewert unter
  `result.parameter`. Einen gescheiterten Schreibversuch nicht als übernommen
  darstellen und nur auf Wunsch wiederholen.
  `kymo_parameter_create` und `kymo_parameter_delete` gelten nur für manuell
  angelegte Parameter (z. B. über CAN, wo die Firmware keine Liste melden kann);
  vom Gerät gemeldete IDs lassen sich weder anlegen noch löschen.
- **Trace:** Session über `kymo_trace_sessions` wählen, explizite `session_id`
  angeben. Analyse liest Auswahl; nur `kymo_trace_select` verändert sie.
  Unbekannte Clock-Metadaten als Ticks behandeln. Lücken/Unsicherheit und
  `truncated` im Ergebnis erhalten; daraus keinen lückenlosen Gesamttrace ableiten.
- **Replay:** Öffnet standardmäßig pausiert. Seek benötigt Session und Position;
  Jobabschluss, `target_reached` und EOF getrennt auswerten.
- **Dateien:** Nur freigegebene lokale Verzeichnisse benutzen. Eindeutige
  Dateinamen bevorzugen; bestehende Dateien nur mit autorisiertem `overwrite: true`
  ersetzen. Größere Daten als Artefakt exportieren statt vollständig in den Kontext
  zu laden. Chrome Trace erfordert verifizierte Ziel-Clock-Metadaten.

Für konkrete Aufrufbeispiele lies [references/workflows.md](references/workflows.md).

## Jobs, Fehler und Abschluss

`job_id` bedeutet Annahme, nicht Erfolg. `kymo_job_get` liefert den Job unter
`data.job`: Zustand aus `data.job.state`, Ergebnis aus `data.job.result` lesen.
Den Job sparsam pollend verfolgen
(gewöhnlich 0,5–1 s), bis `succeeded`, `failed` oder `cancelled`. Ein eigener
Zeitablauf ist keine bestätigte Stornierung; Job-ID und Zustand für Weiterarbeit
erhalten. `kymo_job_cancel` nur bei unterstützter, gewünschter Stornierung nutzen.
Bei unklarer Antwort einer Mutation zuerst Zustand/Job prüfen. Einen
`operation_key` für Wiederholung nur bei Tools verwenden, deren Schema ihn erlaubt;
denselben Key ausschließlich mit identischen Argumenten wiederverwenden.

Bei `UNAUTHORIZED` Aktivierung, Token und Lesemodus prüfen, bei `NOT_READY`
GUI/Quelle/Session prüfen, bei `PATH_DENIED` Freigaben prüfen. Tokeninhalte nicht
ausgeben, in Skills speichern oder in Client-Konfigurationen einbetten.

Berichte den tatsächlich erreichten Zustand, betroffene IDs, abgeschlossene Jobs
und Artefaktpfade. Behaupte verlustfreie Erfassung nur für geprüfte Daten und den
gemessenen Zeitraum; Empfang, Rohpuffer-Eviction und Anzeige-Reduktion unterscheiden.

# Aufrufbeispiele

Toolnamen sind MCP-Namen; der Host kann davor einen Namensraum setzen. IDs aus
vorherigen Antworten übernehmen. Beispielargumente gegen das verbundene Schema
prüfen. `data` in der Antwort enthält das Ergebnis.

## Numerische Demo auf Wunsch

```text
kymo_status({})
kymo_capabilities({})
kymo_connection_types({})
kymo_connection_create({"type":"Test","name":"MCP-Demo","operation_key":"demo-quelle-1"})
kymo_connection_start({"connection_id":"<zurückgegebene ID>"})
kymo_job_get({"job_id":"<Startjob>"})
kymo_signals({})
kymo_values({"signal_ids":["<entdeckte Signal-ID>"]})
kymo_chart_create({"type":"time_series","title":"Messung"})
kymo_job_get({"job_id":"<Renderer-Job>"})
kymo_assignment_set({"signal_id":"<Signal-ID>","chart_id":"<Chart-ID>","value_field":"y"})
```

Jobs vor der abhängigen Operation bis zum Erfolg verfolgen. Signal-ID auf die
gewählte Quelle beziehen. Noch keine Messwerte? Diagnose prüfen und begrenzt warten.

## CSV und kurze Datenabfrage

```text
kymo_samples({"signal_id":"<Signal-ID>","limit":100})
kymo_statistics({"signal_id":"<Signal-ID>"})
kymo_export({"format":"samples_csv","signal_id":"<Signal-ID>","path":"<freigegebener Ordner>/measurement-001.csv","operation_key":"csv-001"})
kymo_job_get({"job_id":"<Exportjob>"})
kymo_artifact_get({"artifact_id":"<Artefakt aus erfolgreichem Job>"})
```

Bei `next_cursor` mit unveränderter Signal-/Snapshot-ID weiterlesen. Exporte
beschreiben die zum Exportzeitpunkt gehaltenen Rohdaten. Die Standardgrenzen sind
20.000 Samples je Signal und 250.000 insgesamt; Eviction ist keine Empfangslücke.
Ein Auftrag für eine Langzeitaufzeichnung wird durch einen einmaligen CSV-Export
des Rohpuffers nicht erfüllt.

## Trace-Aufnahme vollständig beenden

```text
kymo_trace_sessions({})
kymo_capture_start({"session_id":"<verbundene Live-Session>","path":"<freigegebener Ordner>/capture-001.kymotrace"})
# Während Aufnahme nur die von capabilities zugelassenen leichten Tools nutzen.
kymo_diagnostics({})
kymo_capture_stop({})
kymo_job_get({"job_id":"<Capture-Stopjob>"})
# Nach succeeded: Ziel veröffentlicht, Artefakt im Jobresultat.
kymo_connection_stop({"connection_id":"<Quelle>"})
kymo_replay_open({"path":"<freigegebener Ordner>/capture-001.kymotrace","paused":true})
```

Capture-Start braucht eine bereits vorhandene verbundene Live-Session, etwa von
einer KymoTrace-v2-Quelle. Die numerische Testquelle allein erzeugt dafür keine
Trace-Session. Schlägt die Veröffentlichung fehl, zeigt der Job einen Fehler;
die abgeschlossene versteckte `.capture`-Datei bleibt am Zielordner zur Recovery.
Keine „gespeichert“-Meldung ohne erfolgreichen Abschluss.

## Geräteparameter setzen und Bestätigung prüfen (ab KymoStudio 2.7)

```text
kymo_connections({})
kymo_parameters({"connection_id":"<Quelle>"})
# Leere Liste? Einmal neu anfragen und erneut lesen:
kymo_parameters_request({"connection_id":"<Quelle>"})
kymo_parameters({"connection_id":"<Quelle>"})
kymo_parameter_set({"connection_id":"<Quelle>","parameter_id":100,"value":1.5})
kymo_job_get({"job_id":"<Schreibjob>"})
# succeeded = Gerät bestätigt; failed mit DEVICE_REJECTED / DEVICE_NO_ANSWER = nicht übernommen.
# data.job.result.parameter enthält in allen Fällen Gerätewert und Status.
```

Grenzen (`minimum`/`maximum`) und Einheit stammen aus der Firmware. Bei
`DEVICE_REJECTED` den gemeldeten Gerätewert berichten, bei `DEVICE_NO_ANSWER`
nicht als übernommen darstellen und nur auf Wunsch erneut senden. Für Firmware ohne
Selbstmeldung legt `kymo_parameter_create` einen Parameter mit eigener ID,
Name, Einheit und Grenzen an; die Firmware prüft trotzdem jeden Wert.

## Geöffnete Messaufnahme auswerten

```text
kymo_signals({})
# Aufnahme-Signale haben IDs wie rec1-<Quelle>_<n> und „(Aufnahme)“ im Namen.
kymo_statistics({"signal_id":"rec1-<Quelle>_0"})
kymo_samples({"signal_id":"rec1-<Quelle>_0","start":10.0,"end":11.0,"limit":1000})
```

Die Statistik eines Aufnahme-Signals umfasst die gesamte Aufnahme. Große
Bereiche als CSV exportieren statt seitenweise in den Kontext zu laden.

## Workspace und Replay

```text
kymo_workspace_get({})
kymo_chart_update({"chart_id":"<Chart-ID>","title":"Neuer Titel","expected_revision":<aktuelle Revision>})
kymo_workspace_save({"expected_revision":<danach aktuell gelesene Revision>})
kymo_replay_control({"action":"seek","session_id":"<Replay-Session>","position_us":1000})
kymo_job_get({"job_id":"<Seekjob>"})
```

Beim vollständigen Layout-Ersatz `workspace_apply` den gerade gelesenen Workspace
gezielt verändern; `expected_revision` und `replace_existing: true` senden. Bei
Konflikt die GUI-Änderungen berücksichtigen. Nach Seek zusätzlich `target_reached`
und `state.eof` prüfen.

## Geeignete Nutzerprompts

- „Nutze $kymostudio-mcp und prüfe den Status meiner verbundenen Messquellen.“
- „Erstelle für das Signal Temperatur ein Zeitdiagramm, ohne Quellen neu zu starten.“
- „Zeichne diese Live-Trace-Session auf und warte beim Stoppen auf den vollständigen Abschluss.“
- „Exportiere die gehaltenen Messwerte in meinen freigegebenen Ordner und gib den bestätigten Dateipfad aus.“
- „Analysiere den gespeicherten Trace und zeige Lücken oder unbekannte Clock-Domänen ausdrücklich.“
- „Setze kp meines PI-Reglers auf 1.5 und berichte, ob das Gerät den Wert bestätigt.“
- „Werte die geöffnete Messaufnahme aus: Mittelwert und RMS je Signal über die gesamte Aufnahme.“

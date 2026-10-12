# Einreichungsvorbereitung

Stand: **2026-10-12**, Paketkandidat **0.1.1**. Kontakt:
**kontakt@kymotrace.de**, Herausgeber: **Christof Seidel**.

Dies sind vorbereitete Unterlagen. Es wurde kein Portalentwurf angelegt, keine
Einreichung abgeschickt und keine Freigabe oder verifizierte Identität behauptet.
GitHub-Veröffentlichung, lokale Installation und Aufnahme in ein offizielles
Verzeichnis sind getrennte Nachweise.

## Was bereitsteht

- Portable, Codex- und Claude-Manifeste mit übereinstimmender Version, Herausgeber,
  Produktlogo, Startprompts und Verzeichnisbeschreibung.
- Kurzer OpenAI-Untertext innerhalb von 30 Zeichen; relative Iconpfade und
  ein quadratisches SVG mit 64 × 64 Pixeln.
- Paketinterne README, GPL-Lizenz, Datenschutzbeschreibung und Supportkontakt.
- [Formularwerte und Datenfluss](submission.json),
  [Reviewer-Ablauf und Prüffälle](REVIEW.md),
  [Vorab-Anfragen](PROVIDER-INQUIRIES.md).
- Strukturprüfung und Regressionstests. Diese ersetzen keine Portalscans.

Das ZIP enthält den Bedien-Skill. Die erforderliche Desktop-App und ihre lokale
MCP-Verbindung bleiben externe Voraussetzungen. Ein Paket ohne MCP-Deklaration
ist deshalb noch kein Nachweis, dass die Kernfunktion für einen Cloud-Host oder
für OpenAIs regulären Skills-only-Einreichungsweg geeignet ist.

## Claude: Verzeichnis und offizieller Marketplace

Der reguläre Weg führt zum [Entwicklerportal](https://claude.ai/directory/manage):
**Plugin bundle** auswählen, `CodeName-666/kymostudio-agent-plugin` als Repository,
`plugins/kymostudio` als Plugin-Pfad und `feat/official-directory-submission`
als Branch eintragen. Nach einem Merge kann stattdessen `main` verfolgt werden.
Das Portal liest GitHub direkt, kein lokales Client-Kit hochladen.

Vorbereitet sind Listingtext, Kontakt und Datenflussantworten. Im Portal den
passenden Account bzw. die zuständige Organisation wählen, GitHub-Schreibzugriff
verbinden, **Validate** ausführen und blockierende Befunde korrigieren. Jede
Prüfung gilt nur für den gelesenen Commit. Kontakt, Datenhandhabung und die
persönlichen Compliance-Erklärungen vor **Submit for review** prüfen.

Eine Aufnahme in `claude-plugins-official` erfolgt laut aktueller Claude-Code-
Dokumentation über den Anthropic-Partnerkontakt und ist vom Verzeichnisportal
getrennt. Der im offiziellen Repository noch verlinkte Kurzlink führt inzwischen
zur allgemeinen Verzeichnisdokumentation. Dafür ist eine gesonderte Anfrage
vorbereitet; kein Fremd-PR oder Formular wurde abgeschickt.

Quellen: [Claude Code Veröffentlichung](https://code.claude.com/docs/en/plugins/publish),
[Portalablauf](https://claude.com/docs/plugins/submit),
[Verzeichnis-Prüfliste](https://claude.com/docs/plugins/pre-submission-checklist),
[Offizielles Repository](https://github.com/anthropics/claude-plugins-official).

## OpenAI / Codex: lokale Kernfunktion zuerst klären

OpenAI verlangt eine Abstimmung mit dem OpenAI-Ansprechpartner, wenn die
Kernfunktion lokale Ausführung oder Zugriff auf Anwendungen bzw. Hardware
benötigt. Das trifft hier zu. Der reguläre Remote-MCP-Weg erfordert einen
erreichbaren HTTPS-Dienst; KymoStudio bietet derzeit Loopback und einen lokalen
Adapter. Dafür liegt in [PROVIDER-INQUIRIES.md](PROVIDER-INQUIRIES.md) eine Anfrage
für den bestehenden lokalen Bedienweg bereit.

Im [OpenAI-Portal](https://platform.openai.com/plugins) sind außerdem eine
verifizierte Herausgeberidentität und passende Organisationsrechte erforderlich.
Nach bestätigtem Einreichungsweg das neutrale Plugin-ZIP hochladen, Listing und
Skills prüfen, sämtliche verpflichtenden Scans abschließen und erst anschließend
die Prüfung anfordern. Die bloße ZIP-Struktur erlaubt keine Aussage zur Zulassung.

Im öffentlichen Paket wird kein MCP-Server importiert. Deshalb stehen die acht
vorbereiteten Prüffälle außerhalb des Manifests: MCP-Review-Felder sind nicht für
ein Paket ohne deklarierten Server gesetzt. Ein späterer MCP-Reviewweg benötigt
zusätzlich die verlangten ausgeführten Fälle und einen zugänglichen Demo-Nachweis.

Quellen: [Lokale Integrationen und Einreichungswege](https://developers.openai.com/plugins/guides/submit-claude-plugin),
[ZIP, Metadaten und Prüfung](https://developers.openai.com/plugins/deploy/submission),
[Plugin-Richtlinien](https://developers.openai.com/plugins/plugin-guidelines).

## Offene Punkte vor dem tatsächlichen Absenden

| Punkt | Stand / nächster Schritt |
|---|---|
| Einreichungskontakt | Vom Herausgeber angegeben: kontakt@kymotrace.de |
| KymoStudio-Reviewer-Build | Öffentlicher Download oder gesonderter Reviewer-Zugang noch nicht angegeben |
| OpenAI-Zulassung für lokale App | Vorab-Abstimmung erforderlich; Anfrage vorbereitet |
| Anthropic-Account und GitHub-Verbindung | Plan, Rolle und Portalzugriff persönlich prüfen |
| OpenAI-Identität und Organisationsrechte | Im Portal prüfen; keine Bestätigung aus dieser Vorbereitung |
| Anthropic-Portalscan / OpenAI-Scan | Noch nicht ausgeführt |
| Agent-Prüffälle | Vorgeschlagen; reine Pakettests und ein SDK-Smoke-Test ersetzen diese nicht |
| Zielgruppe unter 18 / Supportdaten-Aufbewahrung | Vom Herausgeber vor den Datenfluss-Erklärungen festlegen |
| Produktlogo und Herausgeberrechte | Bestehendes KymoStudio-Artwork verwendet; Rechte im Portal bestätigen |
| Compliance-Erklärungen | Herausgeber liest und bestätigt die dort verlangten Erklärungen |

Es gibt derzeit keinen belegten öffentlichen App-Download. Eine öffentliche
Homepage oder einen Download-Link nicht aus der E-Mail-Domain ableiten.
Die Paket-URLs verweisen auf das öffentliche GitHub-Projekt; die Datenschutzseite
verweist auf diesen Vorbereitungsbranch und muss bei einem Branchwechsel mitziehen.

## Lokal prüfen und ZIP bauen

```sh
python -m unittest discover -s tests -v
python tools/check_submission.py
claude plugin validate plugins/kymostudio --strict
claude plugin validate .claude-plugin/marketplace.json --strict
python tools/package_plugin.py --output dist/submission-0.1.1
```

Für einen vereinbarten ZIP-Upload `dist/submission-0.1.1/kymostudio-plugin.zip`
verwenden. Es enthält den Plugin-Wurzelordner einschließlich Skills und Artwork.
Das zweite ZIP enthält zusätzlich beide Marketplaces und Entwicklungsunterlagen.
Ausgabeordner müssen neu sein. Ohne `--adapter` bauen, damit keine lokalen Pfade
oder Token-Dateireferenzen in ein öffentliches Prüfartefakt gelangen.

Die Strukturprüfung meldet ausdrücklich `provider_review: not_performed`.
Eine grüne lokale Prüfung ist kein Einreichungs- oder Freigabenachweis.

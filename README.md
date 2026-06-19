# FNFsupport Plugin für Modmail.dev

Dieses Plugin fügt dem Modmail.dev Bot den Befehl `.closerequest` hinzu.

## Funktionen
- `.closerequest *reason*`: Sendet eine Anfrage zum Schließen des Tickets an den User.
- Der User kann über Buttons (`Accept` / `Decline`) entscheiden.
- Wenn der User innerhalb von 6 Stunden nicht reagiert, wird das Ticket automatisch geschlossen.
- Alle Nachrichten werden als Embeds gesendet.
- Beim Schließen wird die Begründung automatisch in den Log-Channel gesendet.

## Installation
Verwenden Sie den folgenden Befehl in Ihrem Modmail-Server:
```
?plugin add breadybread123/FNFsupport-plugin/FNFsupport
```
*(Ersetzen Sie `?` durch Ihren Bot-Präfix)*

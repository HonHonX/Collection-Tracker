# Collection-Tracker
Projektarbeit Web Technologie

___

## Git Best Practices
1. Regelmäßige Commits
    - *Kleine, häufige Commits*: Commits sollten möglichst klein und spezifisch sein. Dies erleichtert es, Änderungen nachzuvollziehen und Fehler rückgängig zu machen.
    - *Commit-Nachrichten beschreiben Änderungen*: Verwende prägnante und klare Commit-Nachrichten, die beschreiben, was geändert wurde und warum. Eine gute Nachricht beantwortet in einem Satz: „Was wurde geändert?“.
        - Schlechte Nachricht : `Update files`
        - Gute Nachricht : `Fix bug in user authentication flow`
2. Branch-Management
    - *Arbeite auf separaten Branches*: Vermeide es, direkt auf dem main/master-Branch zu arbeiten. Erstelle stattdessen für jede neue Funktion oder Bugfix einen eigenen Branch (z.B. feature/new-login oder bugfix/fix-typo).
    - *Aussagekräftige Branch-Namen*: Wähle für Branches beschreibende Namen, die den Zweck des Branches klar erkennen lassen.
3. Pull Requests und Code Reviews
    - *Nutze Pull Requests (PRs)*: Bevor Änderungen in den main-Branch gemerged werden, sollte ein Pull Request gestellt werden. Dies ermöglicht anderen Teammitgliedern, deinen Code zu überprüfen.
    - *Kommentiere PRs und Reviews*: Nimm dir Zeit, PRs von Kollegen zu kommentieren und Feedback zu geben. Gute Kommunikation in Reviews verbessert den Code und das Teamwork.
4. Commit-Historie aufräumen
    - *Nutze git rebase statt git merge, wenn möglich*: Um eine saubere Commit-Historie zu behalten, kann git rebase verwendet werden, um Änderungen ohne unnötige Merge-Commits zu integrieren.
    - *Rebase vs. Merge*: Rebase ist gut für die lokale Arbeit, aber wenn du gemeinsam arbeitest, kann merge sicherer sein, um die Historie konsistent zu halten.
5. Konflikte frühzeitig lösen
    - *Konflikte proaktiv angehen*: Wenn es Merge-Konflikte gibt, behebe sie so früh wie möglich. Lass Konflikte nicht unbeachtet, da sie später schwieriger zu lösen sein könnten.
    - *Überprüfe Konflikte vor dem Commit*: Stelle sicher, dass alle Konflikte gelöst sind, bevor du einen Merge oder Rebase abschließt.
6. Pull, bevor du pushst
    - *Pull regelmäßig*: Hole dir regelmäßig die neuesten Änderungen vom Remote-Repository (git pull), bevor du deine eigenen Änderungen hochlädst (git push), um Konflikte zu minimieren.
    - *Pull nach dem Motto*: Aktuelle Basis behalten: Insbesondere wenn du mit mehreren Leuten arbeitest, solltest du sicherstellen, dass deine lokale Version immer aktuell ist.
7. Große Dateien und sensible Daten vermeiden
    - *Keine unnötig großen Dateien*: Lade keine großen Dateien wie Videos oder Binärdateien ins Repository hoch, außer sie sind essenziell für das Projekt.
    - *Sensible Daten nie commiten*: Vermeide es, sensible Daten wie Passwörter, API-Schlüssel oder private Konfigurationsdateien in das Repository zu laden. Nutze .gitignore, um diese Dateien auszuschließen.
8. Nutze .gitignore
    - *Erstelle eine .gitignore-Datei*: Diese Datei bestimmt, welche lokalen Dateien nicht zum Repository hinzugefügt werden sollen. Typische Beispiele sind Konfigurationsdateien, Log-Dateien und Build-Artefakte.
9. Verantwortungsvoller Umgang mit git reset und git force push
    - *Vorsicht bei git reset*: Dieses Kommando kann Änderungen rückgängig machen und sie aus der Historie entfernen. Sei besonders vorsichtig bei der Arbeit mit Teamkollegen.
    - *Force Push vermeiden*: Nutze --force beim Pushen nur, wenn du sicher bist, dass du keine Arbeit anderer überschreibst. Im Zweifel lass es lieber.
10. Commit-Nachrichten im Imperativ schreiben
    - *Benutze den Imperativ*: Schreib Commit-Nachrichten im Befehlsstil, also „Fix bug“ anstatt „Fixed bug“. Das ist gängige Praxis und sorgt für Konsistenz.

___  




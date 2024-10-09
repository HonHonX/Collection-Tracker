## Git Einrichtung
### Am Arbeitsrechner:
1. Proxy setzen , falls noch nicht geschehen (Special Internet Access nötig)
  ```
  git config --global http.proxy http://sia.telekom.de:8080
  git config --global https.proxy https://sia.telekom.de:8080
  ```
2. Navigation ins Zielverzeichnis über `cd`, dann Repository klonen
  ```
  git clone https://github.com/HonHonX/Collection-Tracker.git
  ```
### Privatrechner/VM:
* Siehe Schritt 2
___

## Environment einrichten
Im Anaconda/Miniconda Terminal anlegen über: \
`conda create --name music`\
Beim Start des Terminals muss das Environment jedes mal neu aktiviert werden über:\
`conda activate music`\

Im neuen Environment sollten folgende Libraries/Tools installiert werden:
* `conda install pip`

___

## Was bisher geschah: Bereitstellung über PythonAnywhere

Um den Code deiner Django-App von einem GitHub-Repository auf PythonAnywhere zu beziehen, kannst du die folgenden Schritte befolgen:

1. Repository-URL notieren
* Stelle sicher, dass du die HTTPS-URL deines GitHub-Repositories zur Hand hast. Du findest diese auf der Hauptseite deines Repositories, wenn du auf die grüne Schaltfläche "Code" klickst.
2. Einloggen bei PythonAnywhere
* Logge dich in dein PythonAnywhere-Konto ein und gehe zu deinem Dashboard.
3. Web-App erstellen oder auswählen
* Falls du noch keine Web-App hast, erstelle eine neue Web-App. Wenn du bereits eine Web-App hast, gehe zum Tab "Web" und wähle deine App aus.
4. Konsole öffnen
* Öffne eine Konsole (Shell) in PythonAnywhere:
* Klicke auf den Tab "Consoles" und öffne eine neue Bash-Konsole.
5. Git installieren (falls nötig)
* PythonAnywhere hat Git vorinstalliert. Du kannst dies testen, indem du den Befehl eingibst:
` git --version `
* Wenn du eine Version siehst, ist Git bereits installiert.
6. Code klonen
* Wechsle in das Verzeichnis, in dem du den Code speichern möchtest. Zum Beispiel:
` cd CollectionTracker `
Klonen dein GitHub-Repository mit folgendem Befehl:
` git clone https://github.com/HonHonX/Collection-Tracker.git `
7. Abhängigkeiten installieren
* Wechsel in das Verzeichnis deines geklonten Repositories:
` cd Collection-Tracker `
* Stelle sicher, dass du die notwendigen Abhängigkeiten installierst, indem du Folgendes ausführst:
` pip install -r requirements.txt `
8. Django-Einstellungen anpassen
* Stelle sicher, dass die ALLOWED_HOSTS in deiner settings.py-Datei korrekt konfiguriert ist:
` ALLOWED_HOSTS = ['CollectionTracker.pythonanywhere.com'] `
9. Statische Dateien sammeln
* Führe den Befehl aus, um statische Dateien zu sammeln:
` python manage.py collectstatic `
10. Web-App neu starten
* Gehe zurück zum Tab "Web" auf PythonAnywhere und klicke auf "Reload", um die Änderungen zu übernehmen.
11. Zugriff auf deine App
* Jetzt solltest du in der Lage sein, auf deine App über die URL http://CollectionTracker.pythonanywhere.com zuzugreifen.

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

## Environment A
Im Anaconda/Miniconda Terminal anlegen über: \
`conda create --name music`\
Beim Start des Terminals muss das Environment jedes mal neu aktiviert werden über:\
`conda activate music`\

Im neuen Environment sollten folgende Libraries/Tools installiert werden:
* `conda install pip`

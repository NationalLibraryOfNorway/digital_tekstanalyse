[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/NationalLibraryOfNorway/digital_tekstanalyse/HEAD)
# DHLAB

[Launch NBviewer](https://nbviewer.org/github/NationalLibraryOfNorway/digital_tekstanalyse/tree/main/) 

Nasjonalbiblioteket har utviklet et API (Application Programming Interface) mot tekstene i NB Digital (bøker og aviser) og en funksjonalitet for bruk av API-et i Jupyter Notebook som kan benyttes av forskere. Jupyter Notebook kan benyttes uten kjennskap til programmering. Med API-et er det mulig å studere data fra de digitale tekstene for eksempel ved generering av ordfrekvenslister, konkordanser, kollokasjoner og n-grammer og ved uttrekk av navn og narrative grafer. Alle uttrekk kan gjøres på enkeltverk eller definerte korpus. Bak API-et er det en kobling til metadata slik at korpus kan defineres på bakgrunn av bibliografisk informasjon.

Klikk på "launch binder"-ikonet over for å åpne repositoriet i Binder


## Deploy

Build with jupyter-book. Deploy to gh-pages with ghp-import.

```python
jupyter-book build .
# pip install ghp-import
ghp-import -n -p -f _build/html
```

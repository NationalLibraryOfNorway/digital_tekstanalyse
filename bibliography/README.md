# README

This directory contains the bibliography for dhlab.

To update from Zotero, run the code below in your terminal. 

> **Note:** Ensure LIBRARY_ID and ZOTERO_API_KEY env variables are set in a local .env file.

``` shell
source .env
python zotero_citations_copy.py $LIBRARY_ID group $ZOTERO_API_KEY bibliography.md 
```

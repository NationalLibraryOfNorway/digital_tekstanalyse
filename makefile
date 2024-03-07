all: build serve


build:
	jupyter-book build .

serve:
	ghp-import -n -p -f _build/html
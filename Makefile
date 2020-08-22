SHELL=/bin/bash

install-env:
	conda create -n grt python=3.7
	source activate grt && pip install -r requirements.txt
	conda install ipykernel

uninstall-env:
	conda remove --name grt --all

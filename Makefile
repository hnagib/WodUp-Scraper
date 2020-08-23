SHELL=/bin/bash

install-env:
	conda create -n wodup python=3.7
	conda activate wodup && pip install -r requirements.txt
	conda install ipykernel

uninstall-env:
	conda remove --name wodup --all

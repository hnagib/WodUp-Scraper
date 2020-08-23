SHELL=/bin/bash

install-env:
	conda create -n wodup python=3.7
	source activate wodup && pip install -r requirements.txt
	conda install ipykernel

uninstall-env:
	conda remove --name wodup --all

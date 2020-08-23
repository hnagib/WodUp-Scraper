SHELL=/bin/bash

install-env:
	conda create -n wodup python=3.7
	conda activate wodup && pip install -r requirements.txt
	conda install ipykernel
	python -m ipykernel install --user --name wodup --display-name "wodup"

uninstall-env:
	conda remove --name wodup --all

SHELL=/bin/bash

install-env:
	conda create -n liftpr python=3.7
	source activate liftpr && pip install -r requirements.txt
	conda install ipykernel

uninstall-env:
	conda remove --name liftpr --all

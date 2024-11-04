#!/bin/bash

source venv/bin/activate

python3.9 -m pip install --upgrade pip

python3.9 -m pip install -r requirements.txt 

source actiavte venv

python3.9 server/src/app.py
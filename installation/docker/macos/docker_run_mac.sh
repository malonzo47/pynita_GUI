#!/usr/bin/env bash
docker build . -t pynita

docker run \
    -it \
    -e DISPLAY=docker.for.mac.host.internal:0 \
    --user user \
    -v $(pwd):/app \
    pynita python3 pynita_gui_main.py
    

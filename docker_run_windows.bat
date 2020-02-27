docker build . -t pynita
docker run -it -e DISPLAY=host.docker.internal:0.0 -v %cd%:/app pynita python3 pynita_gui_main.py
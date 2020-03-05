docker build . -t pynita
docker run -it -e DISPLAY=docker.for.win.host.internal:0 -v %cd%:/app pynita python3 pynita_gui_main.py
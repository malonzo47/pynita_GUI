docker run -it \
        -v /tmp/.X11-unix:/tmp/.X11-unix \
        -e DISPLAY=$DISPLAY \
        --user $(id -u) \
        -v $(pwd):/app \
        pynita2 python3 pynita_gui_main.py
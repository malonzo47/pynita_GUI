FROM freelancedev217/pyqtgdal:latest

WORKDIR /app

# build cython functions on startup
CMD cd pynita_source/nita_funs/distance_funs && python3 setup.py build_ext --inplace && cd - && python3 pynita_gui_main.py

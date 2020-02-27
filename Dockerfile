FROM pyqtgdal:latest

# install python packages
# ADD . /app
WORKDIR /app
# ADD requirements.in requirements.in
# RUN pip-compile requirements.in > requirements.txt

# install requirements
# RUN pip3 install -r requirements.txt

# clean the house
# RUN apt-get autoremove -y && \
#     rm /var/lib/apt/lists/* rm -rf /var/cache/apt/*

# compile C code
# WORKDIR /app/pynita_source/nita_funs/distance_funs
# RUN python3 setup.py build_ext --inplace

# compile C code on every run
# WORKDIR /app/pynita_source/nita_funs/distance_funs
# RUN python3 setup.py build_ext --inplace

WORKDIR /app

# startup
CMD cd pynita_source/nita_funs/distance_funs && python3 setup.py build_ext --inplace

brew install python
pip3 install virtualenv
virtualenv venv
source env/bin/activate
pip install --upgrade pip
pip install -r requirements_mac.txt
cd pynita_source/nita_funs/distance_funs
python setup.py build_ext --inplace
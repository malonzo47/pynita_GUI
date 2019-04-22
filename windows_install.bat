set env_name=pynita_env

conda create -n %env_name% python=3.6 --yes && conda activate %env_name% && for /f  "tokens=*" %%i in (requirements.txt) do conda install --yes %%i

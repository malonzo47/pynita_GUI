# pynita_GUI
 **pynita_GUI** is the python implementation of Noise Insensitive Trajectory Algorithm (NITA). Please refer to the [Scientific Reports](https://www.nature.com/articles/srep35129) article for detailed description of NITA and its application. The below steps here will walk you through the installation procedure and package requirements necessary for pynita_GUI. 

 Binary releases are available and it is also possible to run from source.

# Binary distribution (i.e., a simple, double-click executable file)
The binary  of pynita_GUI for Windows and MacOS can be found in [Releases](https://github.com/malonzo47/pynita_GUI/releases).
1. Click on the latest release and then choose the .zip file for your win/mac operating system.
2. Extract that file on your computer and double-click the .exe file to run
3. Demo dataset (point locations, an image stack) can be downloaded from the demo_dataset folder above (3 files).

**NOTE**: The binary releases only work after GDAL installataion. If you do not have or have a different version of GDAL, please make sure to follow the below steps to install the appropriate version of GDAL.

# Prerequisite: GDAL installation
### Windows
1. Download and install Microsoft Visual C++ Redistributable for Visual Studio 2017. 
<https://aka.ms/vs/15/release/VC_redist.x86.exe>
2. Download and install GDAL 3.0.4 Win32.
Downloads can be found in <http://www.gisinternals.com/release.php> and follow the instructions from <https://sandbox.idre.ucla.edu/sandbox/tutorials/installing-gdal-for-windows>

### Mac
Run `brew install gdal` from terminal.

# Running from source
First of all, clone this repository using `git clone`.
## 1. Using Docker
Docker is recommended because you can run pynita_GUI in a dedicated container without any conflicts with your system.
If you do not have Docker installed on your machine, please [install Docker first](https://docs.docker.com/install/). 

Unfortunately, at the moment, there is no universal, out-of-the-box Docker way to show GUI. So we need to use different docker run commands for MacOS, Windows, and Linux.
### Windows
1. Clone the repository 
2. Within the pynita_GUI folder, copy all files from **/installation/docker/windows** to the project root folder (the same level with pynita_gui_main.py)
3. Run CMD (Command) as Administrator then run `prerequisites.bat`.
4. While in CMD, run `docker_run_windows.bat`. This will start the pyNITA program.

### MacOS
1. Copy all files from **/installation/docker/macos** to the project root folder.
2. Run `source prerequisites.sh` from terminal.
3. Open Xquartz by running `open -a xquartz` from terminal and make sure the "Allow connections from network clients" is checked "on". You can find this option in **preferences** menu.
![Xquartz setting on MacOS](images/mac_xquartz.png)
4. Run `source docker_run_mac.sh` from terminal.

### Linux
1. Copy all files from **/installation/docker/linux** to the project root folder.
2. Run `bash docker_run_linux.sh` from terminal.

**NOTE**: For this project, a dedicated docker image (pyqtgdal) was built and available at [DockerHub](https://hub.docker.com/repository/docker/freelancedev217/pyqtgdal).

## 2. Using PIP Without Docker
### Windows
1. Copy all files from **/installation/source/windows** to the project root folder.
2. Run `install_win.bat`.
3. Run `python pynita_gui_main.py`.
4. To build a standalone executable, run `build_release_win.bat`

### Mac
1. Copy all files from **/installation/source/macos** to the project root folder.
2. Run `source install_mac.sh`.
3. Run `python pynita_gui_main.py
4. To build a standalone executable, run `source build_release_mac.sh`

# pyNITA 
 **pyNITA** is the python implementation of Noise Insensitive Trajectory Algorithm (NITA). It can be run from a user-friendly GUI (graphical user interface) or from control scripts. This software is for analysis of satellite imagery time series. One can establish pixel histories at every pixel at every available image date for Landsat imagery (and Sentinel-2 in beta). This can allow for mapping of phenomena such as disturbance (e.g., deforestation, fire), degradation (e.g., drought, charcoal harvest), and recovery.
 
 Please refer to the [Scientific Reports](https://www.nature.com/articles/srep35129) article for detailed description of NITA and its application. The below steps here will walk you through the installation procedure and package requirements necessary for pynita_GUI. 
 
**First, some general resources:**
+ **Demo dataset** (user config file, point locations, an image stack with image dates) can be downloaded from here: https://drive.google.com/file/d/1J8Q1VVfvevbJ5suLHDArOHbOpvu_SKN_/view?usp=sharing
+ **Videos**
    1. **Quick Start:** Watch a video (8 min) that shows basic pyNITA workflow on this demo dataset (https://www.youtube.com/watch?v=dCpLtOsVfC0&t=4s)
    2. **Data prep:** How to make shapefiles of you areas of interest and then use our Google Earth Engine code to extract data to your computer for use in pyNITA (https://www.youtube.com/watch?v=qSG34xOW84k&feature=youtu.be) \
     -- (NOTE): Our standard data-assembly workflow involves Google Earth Engine but users can process image stacks (but not points) without GEE; they just need a valid image stack of spectral indices and an accompanying csv file (single column) containing the dates of each image. \
     -- Link to GEE code for point (aka single pixel) extraction: https://bit.ly/3vvLB1r \
     -- Link to GEE code for polygon (full image stack) extraction: https://bit.ly/3gE8gDm
    3. **DOY Range Example:** How to set day of year ranges to minimize the influence of unwanted “noise” such as phenology, also brief treatment of other key parameters ( https://www.youtube.com/watch?v=Brkor7VwNnU)
    4. **Other key parameters:** Helps you determine when to model pixels using pyNITA for nonlinear processes vs. just using a simple linear fit (https://www.youtube.com/watch?v=090rO5aIj9s)
    5. **pyNITA Parameter Optimization:** This is an **experimental** feature but might help to optimize pyNITA parameters based on hand-drawing a few pixel histories (https://www.youtube.com/watch?v=D7phlqrXF0Y)
+ **Full instructions**. This document gives more detail on key workflows but more importantly, describes each parameter and software output in detail (https://docs.google.com/document/d/1FzLOKcsiEH7lZCHNceFDTj4dbTXjbTXq7-pwwin2Xyw/edit?usp=sharing)
 
 # GETTING STARTED
 Binary releases are available and it is also possible to run from source. \
 **If you don't know what that last line means, you should follow the "Binary distribution" instructions.**

# Binary distribution (i.e., a simple, double-click executable file)
The binary  of pynita_GUI for Windows and MacOS can be found in [Releases](https://github.com/malonzo47/pynita_GUI/releases).
1. Click on the latest release and then choose the .zip file for your win/mac operating system.
2. Extract that file on your computer and double-click the .exe file to run


# STOP HERE UNLESS YOU WANT TO DIG INTO PYTHON CODE

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
First of all, make sure you have Python 3.7.x installed.
You can download Python installer from the [official website](https://www.python.org/downloads/).
To ensure processing big input data, you need to install 64-bit Python. Also, add Python to the system PATH on installation as follows.
![Add Python to PATH](images/python_installation.png)

### Windows
1. Go to subdirectory **/installation/source/windows**.
2. Run CMD (command prompt) **as an administrator**  `install_win32.bat` or `install_win64.bat` depending on your Python architecture.
You can check your Python architecture as follows.
![Python Architecture](images/python_architecture.png)
3. Go back to the root directory that contains `pynita_gui_main.py` and run `python pynita_gui_main.py`.


### Mac
1. Go to subdirectory **/installation/source/macos**.
2. Run `source install_mac.sh`.
3. Go back to the root directory and run `python pynita_gui_main.py`.

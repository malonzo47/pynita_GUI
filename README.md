# pynita_GUI Installation and Requirements
 **pyNITA_GUI** is the python implementation of Noise Insensitive Trajectory Algorithm (NITA). Please refer to the [Scientific Reports](https://www.nature.com/articles/srep35129) article for detailed description of NITA and its application. The below steps here will walk you through the installation procedure and package requirements necessary for pynita_GUI. 

## Python Installation: Windows

**1. Download and unpack the git repository:** You can either download as .zip file or use the git clone option if you are familiar using git. 

**2. Miniconda (Python distribution):** 
 - **a.** Download and install the miniconda distribution for your operating system. Miniconda is a free open-source distribution for Python for package management. Link: https://repo.continuum.io/miniconda/
 - **b.** Launch the windows_install.bat file. It'll create a new miniconda environment under the name pynita_env and do the required package installation.
 
 **3. Launch Pynita** 
 - **a.** Launch the pynita_run.bat to launch pynita_gui_main.py in your python environment.
 
 

## Old Instructions

## Python Installation: Windows/Mac/Linux

The Python installation instructions here are under Anaconda environment. Anaconda is a free open-source distribution for Python and R, most importantly it simplifies package management. 

**1. Download and unpack the git repository:** You can either download as .zip file or use the git clone option if you are familiar using git. 

**2. Ananconda (Python distribution):**

 - **a.**  Download and install Anaconda for your operating system (e.g., Windows/Mac/Linux)
Link: https://www.anaconda.com/distribution/ 

   **b.**	After installation, open Anaconda Navigator and follow the steps below to create a new environment for pynita_gui. The basic idea of creating a new environment is to have an exclusive setup for pynita_gui to function with necessary python packages.
    
   - Click “Environments” on the left panel
   - Click “+ Create” below to create a new environment. 
   - Give a name (e.g., pynita_gui_py36)
   - Under Packages, select Python and from the drop-down, select 3.6 and press Create. Once created, you will see a arrow highlighted next to the environment (e.g., “pynita_gui_py36”)
    
   **c.** Install python packages required by pynita_gui
    - Click on the arrow next to “pynita_gui_py36” in Anaconda Navigator and select “open terminal”
    - From terminal, navigate to downloaded git folder
    
   **d.** Install python packages: List of packages necessary for pynita_GUI are listed in `requirements.txt`
   - Mac/Linux users: Type either, 
            
            while read requirement; do conda install --yes $requirement; done < requirements.txt
            
            OR
            
            cat requirements.txt | while read PACKAGE; do pip install "$PACKAGE"; done
    - Windows users: Type,
        	  
            for /f %i in (requirements.txt) do conda install --yes %i



**3.**	Compile C code:
   - **a.** Mac/Linux users: From terminal, navigate to `pynita_source/nita_funs/distance_funs` folder  and type, `python setup.py build_ext --inplace` to compile the “C” code
   
     **b.** Windows users: For windows users, we have provided compiled "C" code directly, since windows doesn't have an in-built compiler. However, if at the end of the steps, you encounter `distance_funs_cython module not found` error, you will need to compile the "C" code. If you encounter this error, please follow the instructions at the end, to compile "C" code on windows.

     **Caution**: The compiled “C” code in Mac/Linux/Windows is **OS** and **Python version** specific. 

**4.	Install Spyder (python editor)**
- **a.**	Open Anaconda Navigator and select “Home”

  **b.** On the Applications listed, install “Spyder”
  
  **c.** Once installed, click Launch to open Spyder
    
**5. Launch pynita_gui:** – From Spyder, navigate to downloaded git folder and select “pynita_gui_main.py”.

- **a.** From the "Run" menu (NOT the green button) in the taskbar and select "Configuration per file..." or alternatively press Ctrl + F6.
  
  **b.** In the console option, select "Execute in a external system terminal." Click OK.
  
  **c.** Run "pynita_gui_main.py".
  
**6. Start using pyNITA.** - The window may not pop up on top of other windows so you may have to find it.


**Note 1:** Everytime you want to launch pynita_gui, remember to activate the environment (e.g., “pynita_gui_py36”) from Anaconda Navigator and then launch “Spyder”.

**Note 2:** Issue with "Spyder" and a python library "multiprocessing" has been identified. If steps 5a-c are not followed correctly, it may lead to code hanging in the parallelization run phase.


____________________________________________________________________________________________________________________
____________________________________________________________________________________________________________________

**Below here only if you are a Windows user who has encountered the `distance_funs_cython module not found` error**
 
Unlike Mac/Linux, windows do not have an in-built C compiler. Download Visual Studio 2017 from here, https://visualstudio.microsoft.com/downloads/. Use the Community version, which is free. After installation, follow the instructions below,

   - **i.**	Open the Visual Studio Installer.
       
   - **ii.**	Under “Visual Studio Community 2017”, click “Modify”
        
   - **iii.**	Select Individual Components from the top bar. From the subsection listed below, select the following components (7 components) and click “Modify” (bottom right corner)
         
       - **a.**	Compiler, build tools, and runtimes
              - C# and Visual Basic Roslyn compilers
              - VC++ 2017 version 15.9 v14.16 latest v141 tools (Note: Automatically adds another requirement, “Static analysis tools”) 
         
       - **b.**	Development activities
             -	C# and Visual Basic
             -	Visual Studio C++ core features 
            
        - **c.**	SDKs, libraries, and frameworks
              - Windows 10 SDK (10.0.17763.0)
              - Windows Universal C Runtime
           
   - **iv.**	Once installation is complete, from **anaconda terminal of your environment** (see step 3c for the terminal), navigate to `pynita_source/nita_funs/distance_funs` folder and type `python setup.py build_ext --inplace` to compile the “C” code
     

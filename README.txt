author: Mateusz Warkocki
email: mateusz.warkocki@gmail.com

...............................................................................
.........................._..........._.........___............................
........................./ \.........| |...._../ /\)...........................
......................../ = \...___..| |...(_)| |__.____.......................
......................./ ___ \.|___|.| |___| ||  _// =__)......____._..__......
....................../_/...\_\......|_____|_||_|..\____/...../ __ | |/ /......
............................................................./ ___/.\  /.......
............................................................/_/...../_/........
...............................................................................

Welcome to my implementation of artificial life loops. At the beginning it was 
supposed to be only an implementation of SDSR Sayama's loop, however it is
possible to load many transition rule and initial state files.


......................::[ What is needed to run it? ]::........................

Application is written in python and uses OpenCV library.
OpenCV needs Numpy library multiarray support.
Here is quick step by step guide what to do.

---=# Windows x86 #=---

1. Download and install Python 2.7.2 from .msi installer.
   http://www.python.org/getit/
   download link: http://www.python.org/ftp/python/2.7.2/python-2.7.2.msi

2. Download and install OpenCV from .exe installer.
   http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.2/
   file: OpenCV-2.2.0-win32-vs2010.exe
   download link: http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.2/OpenCV-2.2.0-win32-vs2010.exe/download

3. After installing OpenCV go to its folder and copy the contents of Python2.7
   folder to where you installed Python 2.7.2.

4. It might be needed to download and install Numpy
   http://sourceforge.net/projects/numpy/files/NumPy/1.6.0/
   file: numpy-1.6.0-win32-superpack-python2.7.exe
   download link: http://sourceforge.net/projects/numpy/files/NumPy/1.6.0/numpy-1.6.0-win32-superpack-python2.7.exe/download

5. Done. For easier use of python through console add path to python.exe
   to your PATH environmental varaible.


---=# Linux (Ubuntu) #=---

1. Python 2.7 (or 2.6) should be already on board.

2. Install OpenCV for python. Easiest way - from the repository.
   sudo apt-get install python-opencv

3. Done.



............................::[ How to run it? ]::.............................

1. Go to your terminal/console and type:

   python loop.py
   
   where:
     python  - path to your python interpreter (or just like this if you added
               python.exe to PATH or you are working on Linux)
     loop.py - path to the script (or just like this of you are currently in 
               the directory containing the script)
   
   Simple help will be shown.

2. Now try typing:

   python loop.py SDSR-Loop.table.txt
   
   Python will load the script and script will load SDSR-Loop.table.txt file, 
   which contains transition rules. Two windows should poup-up: control panel
   and the environment. More loop table files can be downloaded e.g. from 
   http://code.google.com/p/ruletablerepository/wiki/TheRules

3. If you want to load another loop, it might need different than default
   initial state. You can load it from file using -i option, e.g.
   python loop.py Perrier-Loop.table.txt -i Perrier.initial_state.txt

4. In similar way you can load color files or force to use random colors.
   Script uses random colors by default when it finds out there are more than
   12 states (it has only 12 default colors).



.............................::[ The interface ]::.............................

You can use both - keys and cursor to control the actions.
Respective keys are shown on the buttons. Those which can not be seen are:

 - leff/right arrow - decrease/increase delay [ms] between steps
 - down/up arrow - shrink/enlarge cell matrix by one cell in both dimentions
 - -/+ - shrink/enlarge the scale of cells by one pixel in both dimentions
 - k - for developement - toggle showing keystroke codes
 - f - for developement - toggle showing fps


 
Thank you for using. Feedback will be appreciated!

## Run
* ```python run_trade.py``` - scrape the home page (the default: top report)
* ```python run_trade.py --report banks``` - to scrape a specific report (to get a full list of available reports use: ```--print-reports``` arg)
* ```python run_trade.py --print-reports``` - to print out all available reports

__Output:__
<div>
[INFO] report: mylist
<br>
[INFO] report: top
<br>
[INFO] report: toppct
<br>
[INFO] report: automobilescomponents
<br>
[INFO] report: banks
<br>
[INFO] report: capitalgoods
<br>
and so on ...
<br>
</div>

* ```python run_trade.py --report all``` - scrape all reports.


## Setting up:

__Clean (from scratch):__

* install Python 2.7.12 ( or newer e.g. 2.7.13 ) - https://www.python.org/downloads/release/python-2712/
* WINDOWS: run command line as Administrator and type in : ```pip``` to make sure is installed
if you get an error while running ```pip```, in command line you need to go to C:\Python27\Scripts to install
the following packadges, otherwise you should be able to run it from any directory in the command line. Make sure the command line is started as Administrator
* win: ```pip install lxml==3.6.0```  (other e.g. Mac ```pip install lxml```)
* ```pip install requests```
* ```pip install```
* ```pip install beautifulsoup4```

__Selenium__:
* ```pip install -U selenium```
If it happens that you are on a Windows machine, chromedriver.exe is included in the project.
For OSX, please download chromedriver.exe from https://sites.google.com/a/chromium.org/chromedriver/
and drop it in ```/usr/bin/``` or any dir exists on the PATH


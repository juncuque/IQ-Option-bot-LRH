ECHO OFF
cls

ECHO --------------------------------------
ECHO Installing libraries, this might take a while
ECHO  
ECHO - Even if errors appear, wait until it's over and test if the bot is working properly, if not the case you should search what libraries are missing
ECHO --------------------------------------
ECHO  
pip3 install cryptography
pip3 install uuid
pip3 install boto3
pip3 install numba
pip3 install configparser
pip3 install pickle
pip3 install pstats
pip3 install webbrowser
pip3 install psutil
pip3 install ciso8601
pip3 install numpy
pip3 install talib
ECHO  
ECHO --------------------------------------
ECHO All libraries finished!
ECHO  
ECHO - If the startbot.bat still do not work because of a missing library, search how to install it or try running this .bat again
ECHO --------------------------------------
ECHO  
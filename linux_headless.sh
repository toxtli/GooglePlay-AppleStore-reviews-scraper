#install Xvfb
sudo apt-get install xvfb

#set display number to :99
Xvfb :99 -ac &
export DISPLAY=:99    

#you are now having an X display by Xvfb


#install Xvfb
sudo apt-get update
sudo apt-get install firefox-esr
sudo apt-get install firefox
sudo apt-get install xvfb

#set display number to :99
nohup Xvfb :99 -ac &
export DISPLAY=:99    

#you are now having an X display by Xvfb


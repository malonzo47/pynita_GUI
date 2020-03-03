brew install python
brew install gdal
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" < /dev/null 2> /dev/null ; brew install caskroom/cask/brew-cask 2> /dev/null
brew cask install xquartz

pip3 install virtualenv
virtualenv venv
source env/bin/activate
pip install --upgrade pip
pip install -r requirements_mac.txt
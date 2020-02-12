PYTHON_VERSION=3.6.9
echo "Python version: "
echo $PYTHON_VERSION


cd $HOME
mkdir tmp
cd tmp
wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz
tar zxvf Python-$PYTHON_VERSION.tgz
cd Python-$PYTHON_VERSION
./configure --prefix=$HOME/opt/python-$PYTHON_VERSION
make
make install

# Set aliases for new python and pip
echo "alias python$PYTHON_VERSION=/home/pi/opt/python-$PYTHON_VERSION/bin/python3" >> $HOME/.bashrc
echo "alias pip$PYTHON_VERSION=/home/pi/opt/python-$PYTHON_VERSION/bin/pip3" >> $HOME/.bashrc
source $HOME/.bashrc

# Upgrade pip
pip$PYTHON_VERSION install --upgrade pip



sudo apt-get install mongodb
sudo apt-get install redis-server

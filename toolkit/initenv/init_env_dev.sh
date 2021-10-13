#! /bin/bash

PWD=$(cd `dirname $0`; pwd)
DEP=$PWD/deps

dnf install -y community-mysql-server
systemctl start mysqld
systemctl enable mysqld

dnf install -y redhat-rpm-config
dnf install -y python3-devel
dnf install -y python3-tkinter

pip3 install sqlalchemy

# build and install libta_lib
cd $DEP
tar zxf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure > ta-lib_configure_`date "+%Y-%m-%d_%H-%M-%S"`.log
#mkdir $DEP/libta_lib-devel; ./configure --prefix=$DEP/libta_lib-devel
make -j16 > ta-lib_make_`date "+%Y-%m-%d_%H-%M-%S"`.log
make install > ta-lib_makeinstall_`date "+%Y-%m-%d_%H-%M-%S"`.log
ln -s /usr/local/lib/libta_lib.so.0.0.0 /usr/lib64/libta_lib.so.0

cd $DEP
rm -rf ta-lib

# install TA-Lib
pip3 install TA-Lib

#dnf install python3-matplotlib python3-pandas python3-PyMySQL python3-psutil
pip3 install pandas
pip3 install matplotlib 
pip3 install PyMySQL
pip3 install xlrd
pip3 install psutil

exit

yum install freetype-devel libpng-devel -y #matplotlib

pip3 install --upgrade pip
pip3 install --upgrade setuptools

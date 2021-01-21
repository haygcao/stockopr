for windows:
https://www.lfd.uci.edu/~gohlke/pythonlibs/
TA_Lib-0.4.18-cp38-cp38-win_amd64.whl
> pip install .\TA_Lib-0.4.18-cp38-cp38-win_amd64.whl

for linux:
http://www.ta-lib.org/hdr_dw.html

tar zxf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure
make -j16
make install
ln -s /usr/local/lib/libta_lib.so.0.0.0 /usr/lib64/libta_lib.so.0
cd -
rm -rf ta-lib


tar zxf TA-Lib-0.4.9.tar.gz
cd TA-Lib-0.4.9
python setup.py install
cd -

可以通过 pip install ta-lib 安装

===

mysql
D:\devbin\mysql-8.0.20-winx64

D:\devbin\mysql-8.0.20-winx64\my.ini
[mysql]
default-character-set=utf8

[mysqld]
port = 3306 
basedir=D:\\devbin\\mysql-8.0.20-winx64
datadir=E:\\mysqldata
character-set-server=utf8
default-storage-engine=INNODB
// The server time zone value '�й���׼ʱ��' is unrecognized or represents more than one time zone. 
default-time-zone='+8:00'


D:\devbin\mysql-8.0.20-winx64\bin> .\mysqld --initialize --console
D:\devbin\mysql-8.0.20-winx64\bin> .\mysqld //--daemonize 会使 mysqld 自动退出
D:\devbin\mysql-8.0.20-winx64\bin> .\mysql -u root -p

mysql> ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '111111';
Query OK, 0 rows affected (0.18 sec)

mysql> exit

D:\devbin\mysql-8.0.20-winx64\bin> .\mysqladmin -u root shutdown -p
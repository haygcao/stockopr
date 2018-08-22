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

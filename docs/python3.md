##python3在linux上编译安装
创建python3安装目录
# mkdir /usr/local/python3
下载安装包
# cd /data/app && wget  https://www.python.org/ftp/python/3.6.4/Python-3.6.4.tgz
解压python3安装包
# tar xvf Python-3.6.4.tgz
安装python3依赖包
# yum install gcc-c++ gcc zlib-devel openssl-devel -y
# cd Python-3.6.4
# ./configure --prefix=/usr/local/python3
# make && make install 

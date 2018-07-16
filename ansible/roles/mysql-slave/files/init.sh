#!/bin/bash
#init mysql shell
/usr/share/mysql/bin/mysqld \
--initialize \
--user=mysql \
--datadir=/data/mysql \
--basedir=/usr/share/mysql \
--socket=/var/lib/mysql/mysql.sock

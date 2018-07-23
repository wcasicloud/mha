#!/bin/bash
#
#back mysql sasac databases,
#author liuwei
back_dir=/data/back/`date -d "yesterday" +"%Y/%m"`
if [ ! -d ${back_dir} ]; then
	mkdir -pv ${back_dir}
fi
	/usr/share/mysql/bin/mysqldump --lock-all-tables -uxxx -pxxxx  database  > ${back_dir}/yw_sc.sql
pushd ${back_dir}
if [ -f casicloudyw_sc.sql ]; then
	tar zcvf "casicloudyw_sc-`date -d "yesterday" +"%Y%m%d"`.tar.gz"  sc.sql
	rm -rf casicloudyw_sc.sql

fi
popd

HOST=10.153.40.212:4521
USER=xxx
PASS=xxx
casicloudyw_sc_sql="csc-`date -d "yesterday" +"%Y%m%d"`.tar.gz"
year_str=`date -d "yesterday" +%Y`
month_str=`date -d "yesterday" +%m`
LCD=/data/back/${year_str}/${month_str}
RCD=htyunlu

put_file() {
	lftp -c "set ftp:list-options -a;
	open ftp://$USER:$PASS@$HOST;
	lcd $LCD;
	cd  $RCD;
	mkdir -p uc_sql/${year_str}/${month_str};
	cd uc_sql/${year_str}/${month_str};
	put ${casicloudyw_sc_sql}"
}

if [ -f $LCD/${casicloudyw_sc_sql} ]; then
	put_file
fi

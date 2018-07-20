## 问题描述，从库SQL线程一直处于连接状态
Last_IO_Error:
Last_SQL_Errno: 1061
Last_SQL_Error: Error 'Duplicate key name 'i_index'' on query. Default database: 'test'. Query: 'create unique index i_index on t(id)'

## 解决方法一
停止slave进程
* mysql> stop slave;
设置事物号，事物号在日志里可以找到，在session里设置gtid_next,即跳过这个gitd
* mysql>SET @@SESSION GTID_NEXT='8f9e146f-0a18-11e7-810a-0050568833c8:4';
设置空事物
* mysql>BEGIN;COMMIT;
恢复事物号
* mysql>SET SESSION GTID_NEXT=AUTOMATIC
启动slave进程
* mysql>start slave;

## 解决方法二 (重置master跳过错误)
* mysql>stop slave;
* mysql>RESET MASTER;
* mysql>SET @@GLOBAL GTID_PURGED='8f9e146f-0a18-11e7-810a-0050568833c8:4';
* mysql>START SLAVE;

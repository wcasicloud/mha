==
mysql主从复制：基于gtid的主从复制，并行复制，半同步 ,mha高可用
#一、主从复制用途以及条件
> 1、实时灾备，用于故障切换
> 2、读写分离，提供查询服务
> 3、备份，避免影响业务

#二、主从部署必要条件
> 1、主库开启binlog日志 (设置log-bin参数)
> 2、主从server-id 不同
> 3、从库服务器能连接主库

#三、主从复制原理
> 1、从库生成两个线程，一个I/O线程，一个SQL线程
> 2、I/O线程去请求主库的binlog,并且的到bin-log日志写到relay-log中
> 3、主库会生成一个log dump线程，用来给从库传binlog日志
> 4、SQL线程会读取中继日志文件，并解析成具体的操作执行，这样主从的数据一致，最最终的数据也就一致

#四、主从复制的问题以及解决办法
* 存在问题
> 1、主库宕机之后，数据可能会丢失
> 2、从库只有一个SQL线程，主库写压力大，复制可能超时

* 解决办法
> 1、半同步复制，解决数据丢失问题
> 2、并行复制，解决从库复制延时问题

## 1、mysql AB主从复制,gtid主从复制，并行复制，半同步复制(mysql数据库版本要一致，或者slave版本比master版本高)
master配置

# cat <<EOF > /etc/my.cnf
[client]
port=3306
socket=/var/lib/mysql/mysql.sock
[mysqld]
basedir=/usr/share/mysql
datadir=/data/mysql
socket=/var/lib/mysql/mysql.sock
user=mysql
lower_case_table_names=1
server_id=2
relay-log=/data/mysql/logs/relay-log
log-bin=/data/mysql/logs/bin-log
expire_logs_days=15

rpl_semi_sync_master_enabled = 1
rpl_semi_sync_slave_enabled = 1
slave-parallel-type=LOGICAL_CLOCK
slave-parallel-workers=16
master_info_repository=TABLE
relay_log_info_repository=TABLE
relay_log_recovery=ON

gtid_mode=ON
enforce_gtid_consistency=ON
#### memory configure
innodb_buffer_pool_size=8G
sort_buffer_size=4M
innodb_file_per_table=1
max_connections=3000
[mysqld_safe]
log-error=/var/log/mysqld.log
pid-file=/var/run/mysqld/mysqld.pid
EOF

授权从库连接账户，并给予权限
# mysql> grant replication slave on *.* to ha@'172.25.5.%' identified by 'halo';
# mysql> Flush privileges;

安装半同步复制模块,用mha高可用，所以master和slave都进行了安装，主库切换后，另外一个就成为了从库
# mysql> install plugin rpl_semi_sync_master soname 'semisync_master.so';
# mysql> set global rpl_semi_sync_master_enabled=ON;
# mysql> install plugin rpl_semi_sync_slave soname 'semisync_slave.so';
# mysql> set global rpl_semi_sync_slave_enabled=ON;

slave配置
# cat <<EOF > /etc/my.cnf
[client]
port=3306
socket=/var/lib/mysql/mysql.sock
[mysqld]
basedir=/usr/share/mysql
datadir=/data/mysql
socket=/var/lib/mysql/mysql.sock
user=mysql
server_id=3
expire_logs_days=15

rpl_semi_sync_master_enabled = 1
rpl_semi_sync_slave_enabled = 1
slave-parallel-type=LOGICAL_CLOCK
slave-parallel-workers=16
master_info_repository=TABLE
relay_log_info_repository=TABLE
relay_log_recovery=ON

gtid_mode=ON
enforce_gtid_consistency=ON
#### memory configure
innodb_buffer_pool_size=8G
sort_buffer_size=4M
innodb_file_per_table=1
max_connections=3000
[mysqld_safe]
log-error=/var/log/mysqld.log
pid-file=/var/run/mysqld/mysqld.pid
EOF

安装半同步复制插件
# mysql> install plugin rpl_semi_sync_master soname 'semisync_master.so';
# mysql> set global rpl_semi_sync_master_enabled=ON;
# mysql> install plugin rpl_semi_sync_slave soname 'semisync_slave.so';
# mysql> set global rpl_semi_sync_slave_enabled=ON;

连接master库
# mysql> change master to  master_host='172.25.5.2',master_user='ha',master_password='Lockey+123',master_auto_position=1;

在master上进行数据库操作
# mysql>  select * from gtid_executed;
然后在slave的数据库上通过以下命令查看结果
# mysql> select * from gtid_executed;
# mysql> start slave;

## 2、mha高可用gtid主从，半同步复制集群
* 安装mha相关组件需要安装perl依赖的包
* 在所有节点上需要安装mha-node
* 在mha-manager上需要安装mha-manager和mha-node
1、关于MHA
MHA是一种开源的MYSQL高可用程序，它为MYSQL主从复制架构了提供了automating master failover功能，MHA在监控到master节点故障时，会提升其中拥有最新数据的slave节点成为新的master节点，在此期间，MHA会通过其他从节点获取额外信息来避免一致性方面的问题。MHA还提供了master节点的在线切换功能，即按需切换master/slave节点。
MHA服务有两种角色，mha-manager和mha-node节点

MHA提供了很多工具程序
# manager节点
- masterha_check_ssh：MHA依赖的ssh环境监测
- masterha_check_repl： mysql主从复制监测
- masterha_manager：MHA服务主程序启动
- masterha_check_status：MHA运行状态探测
- masterha_master_monitor：mysql master可用性监测
- masterha_conf_host：添加或删除配置节点
- masterha_stop：关闭MHA服务
- masterha_master_switch：master 节点切换
# node节点
- save_binary_logs：保存和复制master的二进制日志
- apply_diff_relay_logs：识别差异的中继日志事件并应用于其他slave
- filter_mysqlbinlog: 去除不必要的ROLLBACK事件
- purge_relay_logs：清除中继日志事件

2、安装配置MHA
MHA集群中各节点彼此之间均需要基于ssh互信通信，以实现远程控制及数据管理功能。
* 在每个节点上生成ssh密钥，配置ssh互信
* 安装mha-manager,perl依赖包，mha-node
* 编写配置文件
* 检测ssh互信和主从复制环境是否OK
* 启动MHA
(注：如果实现vip漂移，需要在master上配置VIP，manager上需要主从切换脚本)

授权帐号,在master授权即可
# mysql>grant all on *.* to 'mh'@'10.153.%.%' identified by 'wHfDaRs3a';
# mysql>flush privileges;

MHA配置文件
# cat << EOF > /etc/masterha/app1.cnf
server default]
user=mh
password=wHfDaRs3a
manager_workdir=/data/masterha/app1
manager_log=/data/masterha/app1/manager.log
remote_workdir=/data/masterha/app1
ssh_user=root
repl_user=repl_user
repl_password=UBAwlPavw==
ping_interval=1
master_ip_failover_script=/data/masterha/app1/master_ip_failover
master_ip_online_change_script="/data/masterha/app1/master_ip_online_change"
report_script="/data/masterha/app1/mha_send_report.py"

[server1]
hostname=10.153.40.204
master_binlog_dir=/data/mysql/logs
candidate_master=1

[server2]
hostname=10.153.40.205
master_binlog_dir=/data/mysql/logs
candidate_master=1

[server3]
hostname=10.153.40.206
master_binlog_dir=/data/mysql/logs
no_master=1
EOF

# masterha_check_ssh --conf=/etc/masterha/app1.cnf
# masterha_check_repl --conf=/etc/masterha/app1.cnf
# nohup masterha_manager  --conf=/etc/masterha/app1.cnf > /data/masterha/app1/master.log 2>&1 &

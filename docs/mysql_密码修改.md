方法一：适用于管理员或者全局管理员权限的用户
mysql>use mysql;
mysql> UPDATE user SET password=PASSWORD("new password") WHERE user='username';
mysql> FLUSH PRIVILEGES;
mysql> quit;
mysql>update mysql.user set  authentication_string=password('HTiiot@123') WHERE user='root';

mysql>GRANT ALL ON *.* TO 'root'@'%' IDENTIFIED BY 'HTiiot@123';

方法二：
mysql -u root -p
mysql>use mysql;
mysql> SET PASSWORD FOR   username=PASSWORD('new password');
mysql> QUIT

方法三：
#mysqladmin -u root "old password" "new password"


mysql>ALTER USER 'root'@'localhost' IDENTIFIED BY 'Root@1234';

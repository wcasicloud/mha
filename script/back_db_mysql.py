#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tarfile
import datetime
import json
import subprocess
import requests
import time


user = 'mh'
password = 'PqEbLJ+w'
now = datetime.datetime.now()
mm = now.strftime('%Y/%m/')
mysql_db = {'cloudmarketing': '/mnt/ftp/cm_sql/' + mm,
            'cloud_business': '/mnt/ftp/invoice_sql/' + mm,
     #       'choujiang': '/mnt/ftp/choujiang/' + mm,
     #       'fenghui': '/mnt/ftp/fenghui/' + mm,
     #       'jumpserver': '/mnt/ftp/jumpserver/' + mm,
     #       'three': '/mnt/ftp/three/' + mm,
     #       'yunwang_weixin': '/mnt/ftp/yunwang_weixin/' + mm,
     #       'zentao_open': '/mnt/ftp/zentao_open/' + mm
            }
mysql_ip = " -h 10.153.40.206 "


def to_weixin(message):
    corpid = "wx5df6865"
    secret = "_qqlL4zS9Nf3noK4FjHj9hdc9Ih"
    token_url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    playload = {'corpid': corpid, 'corpsecret': secret}
    r = requests.get(token_url, params=playload)
    access_token = r.json()['access_token']
    message = message
    data = {"toparty": "4", "msgtype": "text", "agentid": 1000003, "text": {"content": message}}
    send_message_url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + access_token
    send_message = requests.post(send_message_url, data=json.dumps(data))
    if send_message != 'ok':
        pass


def dump_db():
    message = ""
    for dbname, dbpath in mysql_db.items():
        if not os.path.exists(dbpath):
            os.makedirs(dbpath)
        filename = now.strftime(dbpath + dbname + '_%Y%m%d%H%M%S.sql')
        dumpcmd = "/usr/share/mysql/bin/mysqldump -u " + user + " -p" + password + mysql_ip + dbname + " > " + filename
        subprocess.run(dumpcmd, shell=True)
        tarname = now.strftime(dbpath + dbname + '_%Y%m%d%H%M%S.tar.gz')
        tar = tarfile.open(tarname, "w|gz")
        tar.add(filename)
        tar.close()
        os.remove(filename)
        if  os.path.exists(tarname) is True:
            fsize = os.path.getsize(tarname)
            fsize = fsize / float(1024 * 1024)
            fsize = round(fsize, 2)
            tarname = tarname.split('/')[-1]
            message += u'备份数据库名称：%s\n备份状态：正常\n备份文件名：%s\n备份文件大小：%sMB\n\n' % (dbname, tarname, fsize)
        else:
            message += u'备份数据库名称：%s\n备份状态：失败\n' % (dbname)
    to_weixin(message)


def delete_file(beftime):
    for x in mysql_db.values():
        for i in os.listdir(x):
            filename = x + os.sep + i
            if os.path.getmtime(filename) < beftime:
                try:
                    if os.path.isfilie(filename):
                        os.remove(filename)
                except:
                    pass


if __name__ == '__main__':
    bretime = time.time() - 3600 * 24 * 90
    dump_db()
    delete_file(bretime)

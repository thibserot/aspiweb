#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb,urllib2


def connectToDB():
    conn = MySQLdb.connect( host = "localhost",
                            user = "user",
                            passwd = "password",
                            db = "webaspi")
    return conn

def initDB():
    conn = connectToDB()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS `urls` (
                `url` varchar(255) NOT NULL,
                `status` int(11) NOT NULL DEFAULT '0',
                UNIQUE KEY `url` (`url`));""")
    c.close()
    conn.commit()
    conn.close()


def readURL(url, encoding=""):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'ThibanirBot')]
    req =  opener.open(url)
    htmlSource = req.read()
    if encoding == "":
        encoding=req.headers['content-type'].split('charset=')[-1]
    
    if encoding == "text/html":
        return htmlSource
    try:
        htmlSource = unicode(htmlSource,encoding)
    except UnicodeEncodeError:
        htmlSource = unicode(htmlSource,"latin-1")

    return htmlSource

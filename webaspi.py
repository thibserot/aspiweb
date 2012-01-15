#!/usr/bin/python
# -*- coding: utf-8 -*-

import re,sys,Queue,threading,time,random,os.path
from common import *


urls = Queue.Queue()
NUM_THREADS = 4
TIMEOUT = 60
ENCODING = ""
OUTPUT_DIR = "./"
SAVE_URL_DIR = OUTPUT_DIR + "save/"
URL_WEBSITE = ""


def aspiWeb():
    conn = connectToDB()
    c = conn.cursor()
    while True:
        url = urls.get(True,TIMEOUT)
        print "Downloading",url
        htmlSource = readURL(url,ENCODING)
        path = SAVE_URL_DIR + url[url.find("//")+2:]
        if path[-1] == "/":
            path = path + "index.html"

        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        f = open(path,"w")
        f.write(htmlSource)
        f.close()

        listUrls = re.findall("<a.*href=[\"']([^\"']*)[\"']",htmlSource,re.I)
        #print listUrls
        for u in listUrls:
            if u.find("//") == -1:
                u = URL_WEBSITE + u
            #print url
            if u[0:len(URL_WEBSITE)] != URL_WEBSITE:
                continue
            try:
                c.execute("INSERT INTO urls(url) VALUES(%s)",[u,])
                urls.put(u)
                conn.commit()
            except MySQLdb.IntegrityError:
                pass
                #print sys.exc_info()
            c.execute("UPDATE urls SET status = 1 WHERE url = %s",[url,])
            conn.commit()

        urls.task_done()
        time.sleep(random.randint(10, 100) / 1000.0)


if len(sys.argv) == 2:
    URL_WEBSITE = sys.argv[1]
else:
    print "Usage :",sys.argv[0],"website"
    sys.exit(0)
conn = connectToDB()
c = conn.cursor()
c.execute("SELECT url FROM urls WHERE status = 0")
for r in c:
    urls.put(r[0])
c.close()
conn.close()

if URL_WEBSITE[:-1] != "/":
    URL_WEBSITE = URL_WEBSITE + "/"

if URL_WEBSITE.find("//") == -1:
    URL_WEBSITE = "http://" + URL_WEBSITE

if urls.empty():
    urls.put(URL_WEBSITE)

for i in range(NUM_THREADS):
    print "Spawning thread",i
    t = threading.Thread(target=aspiWeb)
    t.daemon = True
    t.start()

time.sleep(5)
urls.join()
print "End of execution"

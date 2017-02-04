#!/usr/bin/python
# coding: utf-8
from twisted.internet import task
from twisted.internet import reactor
import MySQLdb
import sms
import subprocess
import time

global l
timeoutsms = 2.0 # 2 secondes
timeoutussd = 5.0 # 10 secondes

def SmsSender():
    dbConn = MySQLdb.connect("localhost","dbuser","dbpasswd","dbname") or die ("could not connect to database")
    cursor = dbConn.cursor()
    cursor.execute("""SELECT id, tel, msg FROM sms WHERE status='0'""")
    resultat = cursor.fetchone()
    if resultat is not None:
        idMSG = resultat[0]
        tel = resultat[1]
        msg = resultat[2]
        result = sms.send_sms(msg,tel)
        if result == "Success":
            cursor.execute("""UPDATE `sms` SET `status`=1 WHERE `id`=%s"""%(idMSG))
            dbConn.commit()
    dbConn.close()
    pass

def BalanceChecker():
    try:
    	cmd1 = subprocess.Popen(["/usr/bin/gsm-ussd"], stdout=subprocess.PIPE, stderr = subprocess.PIPE)
    	output1 = cmd1.communicate()[0].split('.')[0]
    	time.sleep(2)
    	cmd2 = subprocess.Popen(["/usr/bin/gsm-ussd","-c"], stdout=subprocess.PIPE, stderr = subprocess.PIPE)
    	time.sleep(2)
        if len(output1) != 0 :
            dbConn = MySQLdb.connect("localhost","dbuser","dbpasswd","dbname") or die ("could not connect to database")
            cursor = dbConn.cursor()
            cursor.execute("""UPDATE `projet_aie`.`credit` SET `montant_credit` ='%s' WHERE `credit`.`id` = 1"""%(output1)) 
	    dbConn.commit() 
	    dbConn.close()  
        pass
    except:
	pass  

l = task.LoopingCall(SmsSender)
g = task.LoopingCall(BalanceChecker)
l.start(timeoutsms)
g.start(timeoutussd,False)
reactor.run()

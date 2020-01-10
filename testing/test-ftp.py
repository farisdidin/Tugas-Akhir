import ftplib
import sys
import time
session = ftplib.FTP('10.199.16.68')
session.login(user='didin', passwd='Tadidin23!')

argument = sys.argv

for i in range(int(argument[1])):
    f = open('test3.txt', "a+")
    f.write('file kedua number : '+str(i+1)+'\n')
    f.close()
    file = open('test3.txt','rb')                  # file to send
    session.storbinary('STOR uploads/repo_2/test3.txt', file)     # send the file
    file.close()
    time.sleep(1)                                    # close file and FTP

session.quit()

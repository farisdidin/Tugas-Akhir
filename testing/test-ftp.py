import ftplib
session = ftplib.FTP('10.199.16.68')
session.login(user='didin', passwd='Tadidin23!')

file = open('test3.txt','rb')                  # file to send
session.storbinary('STOR test3.txt', file)     # send the file
file.close()                                    # close file and FTP
session.quit()

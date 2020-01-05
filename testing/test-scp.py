from paramiko import SSHClient
from scp import SCPClient
import sys, time

argument = sys.argv

ssh = SSHClient()
ssh.load_system_host_keys()
ssh.connect('10.199.16.68', username='didin', password='Tadidin23!')

#SCPCLient takes a paramiko transport as an argument
scp = SCPClient(ssh.get_transport())

# scp.put('test.txt', 'test2.txt')
# scp.get('test2.txt')

# Uploading the 'test' directory with its content in the
# '/home/user/dump' remote directory
for i in range(int(argument[2])):
    f = open(argument[1], "a+")
    f.write('file kedua number : '+str(i+1)+'\n')
    f.close()
    scp.put(argument[1], recursive=True, remote_path='/home/didin/repo-local/test_1')
    time.sleep(1)
    

scp.close()
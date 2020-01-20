from paramiko import SSHClient
from scp import SCPClient
import sys, time
import fileinput

argument = sys.argv

ssh = SSHClient()
ssh.load_system_host_keys()
ssh.connect('10.199.16.68', username='didin', password='Tadidin23!')

#SCPCLient takes a paramiko transport as an argument
scp = SCPClient(ssh.get_transport())


for i in range(int(argument[2]), int(argument[3])):
    with fileinput.FileInput(argument[1], inplace=True,) as file:
        for line in file:
            print(line.replace('ip address 10.199.4.'+str(i), 'ip address 10.199.4.'+str(i+1)), end='')

    scp.put(argument[1], recursive=True, remote_path='/home/didin/REPO/uploads/test_response2/test')
    time.sleep(1)
    print(i)
    

scp.close()
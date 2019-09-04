import subprocess
command = ['git','--git-dir','./config/ftp/R1/.git', 'log']
result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
result = result.stdout.decode('utf-8')
print(result)
print(type(result))

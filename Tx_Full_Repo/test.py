import subprocess

x = subprocess.run([iperf -c 10.0.0.16 -u -p 10002 -t 1])
print(x)
print(x.args)
print(x.returncode)
print(x.stdout)
print(x.stderr)

import fabric.api as fab
import fabric.utils
from fabric.api import run, env, execute, roles, settings, hide
from fabric.context_managers import cd
import time



#env.hosts={'debian@10.8.10.5'}
#env.roledefs = { 'vlc1': ['debian@10.8.10.5'], 'vlc2': ['debian@10.8.10.8'] }
#env.passwords = { 'debian@10.8.10.5:22':'temppwd', 'debian@10.8.10.8:22':'temppwd' }

#nice workaround solution to embed the host access parameters as a fabric task
@fab.task
def vlc1():
    env.hosts={'debian@10.8.10.5'}
    env.passwords = {'debian@10.8.10.5:22':'temppwd'}

@fab.task
def vlc2():
    env.hosts={'debian@10.8.10.8'}
    env.passwords = {'debian@10.8.10.8:22':'temppwd'}

@fab.task
def getRSSI():
    output=fab.sudo("python3 getRSSI.py")
    return output
"""
Wishful Mininet integration
"""

import logging
import os
import subprocess
import re

__author__ = "Zubow"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{zubow}@tkn.tu-berlin.de"


class WishfulNode( object ):
    """A Wishful node is either a Wishful agent or controller."""

    def __init__( self, network_node, script, config, verbose, logfile ):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))

        self.network_node = network_node
        self.script = script
        self.config = config
        self.verbose = verbose
        self.logfile = logfile
        self.ctrl_ip = '127.0.0.1'
        self.ctrl_dl_port = 8989
        self.ctrl_ul_port = 8990

        self.log.info('Starting Wishful script: %s / %s' % (self.script, self.config))

    def start( self ):
        """Start agent or controller.
           Log to /tmp/*.log"""

        if self.verbose:
            verbose_str = '--verbose'
        else:
            verbose_str = ''
        # exec on network node
        self.network_node.cmd( self.script + ' ' + verbose_str + ' --logfile ' + self.logfile + 
        ' --config ' + self.config + ' &' )
        self.execed = False

    def stop( self ):
        """Stop controller."""
        self.network_node.cmd( 'kill %' + self.script )
        self.network_node.cmd( 'wait %' + self.script )

    def find_process( self, process_name ):
      ps = subprocess.Popen("ps -eaf | grep -v grep | grep " + process_name, shell=True, stdout=subprocess.PIPE)
      output = ps.stdout.read()
      ps.stdout.close()
      ps.wait()

      return output

    # This is the function you can use
    def check_is_running( self ):
      output = self.find_process( self.script )

      if re.search(self.script, output) is None:
        return False
      else:
        return True

    def read_log_file( self ):
        fid = open(self.logfile)
        content = fid.read()

        return content

class WishfulAgent( WishfulNode ):
    """The Wishful agent which is running on each wireless node to be controlled."""

    def __init__( self, network_node, script, config, verbose=False, logfile=None ):
        if logfile is None:
            logfile = '/tmp/agent_' + network_node.name + '.log'
        WishfulNode.__init__( self, network_node, script, config, verbose, logfile )
        #self.checkListening()

    def start( self ):
        print("Start Wishful agent.")
        WishfulNode.start(self)

    def stop( self ):
        print("Stop Wishful agent.")
        WishfulNode.stop(self)

class WishfulController( WishfulNode ):
    """The Wishful controller which is communicating with Wishful agents in order to control wireless nodes."""

    def __init__( self, network_node, script, config, verbose=False, logfile=None ):
        if logfile is None:
            logfile = '/tmp/controller_' + network_node.name + '.log'
        WishfulNode.__init__( self, network_node, script, config, verbose, logfile )
        #self.checkListening()

    def start( self ):
        print("Start Wishful controller.")
        WishfulNode.start(self)

    def stop( self ):
        print("Stop Wishful controller.")
        WishfulNode.stop(self)
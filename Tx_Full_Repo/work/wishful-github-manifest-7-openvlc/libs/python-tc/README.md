Introduction
============

About python-tc
---------------------
python-tc provides easy way to configure Traffic-Control subsystem in Linux 

Installing via pip
------------------

    % pip install ./python-tc
    % pip uninstall python-tc

Compiling from source
---------------------

You can compile `python-tc` in the usual distutils way:

    % cd python-tc
    % python setup.py build
    % python setup.py install

Once everything is in place you can fire up python to check whether the
package can be imported:

    % sudo python
    >>> import pytc
    >>>

Of course you need to be root to be able to use iptables and netlink.


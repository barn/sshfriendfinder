#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# -----------------------------------------------------------
# Filename      : sshfriendfinder.py
# Description   : Find ssh keys, and see where you can get with them.
# Requires:     : ag/silver searcher, paramiko via pip.
# Created By    : Ben Hughes <ben@mumble.org.uk>
# Date Created  : 2015-05-30 12:55
#
# License       : MIT
#
# (c) Copyright 2015, all rights reserved.
# -----------------------------------------------------------
import argparse
import os
import subprocess
import sys

import paramiko


__author__ = "Ben Hughes"
__version__ = "0.1"


class Person(object):

    def __init__(self, name):
        self.name = name
        self.keys = {}

    def loadkey(self, keyfile):
        """
        populate the keys list with valid loaded passwordless keys
        """

        if os.path.isfile(keyfile):
            k = loadkeyfile(keyfile)
            if k:
                self.keys[keyfile] = k

    def try_host(self, host):

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        for filename, k in self.keys.iteritems():

            idout = ''

            try:
                ssh.connect(host, username=self.name,
                            pkey=k, look_for_keys=False, allow_agent=False)
                stdin, stdout, stderr = ssh.exec_command('/usr/bin/id')
                stdin.close()
                idout = stdout.read()

            except paramiko.ssh_exception.AuthenticationException, e:
                # Didn't authenticate, which is good!
                print "Failed to auth with %s, this is good" % e
                continue
            except Exception, e:
                print "It broke with %s" % e
                continue

            ssh.close()
            if idout != '':
                # print k.get_name() + " " + k.get_base64() + " " + filename
                print "'%s' will get you on to %s as %s" % (filename,
                                                            host, self.name)


def loadkeyfile(privatekeyfile):
    """
    Try to load a key, based on all the types in order of liklihood.
    """

    key = False

    for keyloader in [paramiko.RSAKey.from_private_key_file,
                      paramiko.DSSKey.from_private_key_file,
                      paramiko.ECDSAKey.from_private_key_file]:
        try:
            key = keyloader(privatekeyfile)
        except paramiko.ssh_exception.PasswordRequiredException:
            continue
        except paramiko.ssh_exception.SSHException:
            continue

    return key


def findkeys(dir):
    """
    This requires ag/the silver searcher.

    given a dir, find all the keys in it.
    """
    cmd = ['ag', '-l', '--nocolor', '--', '-----BEGIN .* PRIVATE KEY-----', dir]
    try:
        return subprocess.check_output(cmd).rstrip().split("\n")
    except OSError:
        sys.exit("Unable to find 'ag', which this uses.")


def do_homedir(user, hosts=None):

    p = Person(name=user)

    sshdir = os.path.expanduser('~%s/.ssh' % user)
    if not os.path.isdir(sshdir):
        print "Can't find an SSH dir of '%s'" % sshdir
        return

    map(lambda x: p.loadkey(x), findkeys(sshdir))

    # only bother continuing if we found any.
    if not p.keys:
        print "Can't find any SSH keys of use in '%s'" % sshdir
        return

    if hosts is None:
        hosts = ['127.0.0.1']

    # hosts = ['127.0.0.1', 'bastion.example.org', 'fw.example.org']
    for host in hosts:
        print "Trying against %s:" % host
        p.try_host(host)


if __name__ == "__main__":

    p = argparse.ArgumentParser(description='Find me some SSH keys,\
        and play with them')

    p.add_argument('--home', '-H', metavar='davedave',
                   help='Run against user\'s SSH dir')

    p.add_argument('--tryhost', '-t', metavar='host.example.org', nargs='+',
                   help='add a host to try against')

    args = p.parse_args()

    if args.home:
        do_homedir(args.home, args.tryhost)
    else:
        p.print_help()

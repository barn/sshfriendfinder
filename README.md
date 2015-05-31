# sshfriendfinder

Run it (as root) to find all the SSH keys a user has a shared system, and then try them as that user on a bunch of places.

This is so you can find when people don't add passphrases to things, for use in lateral movement &c.

# Requirements

* [Paramiko](http://www.paramiko.org/) for Python.
* [ag/the silver searcher](http://betterthanack.com/) for lazy searching.

# Using

To try all the keys davedave has, just against localhost, do:

```
root# python sshfriendfinder.py -H davedave
Trying against 127.0.0.1
'/Users/davedave/.ssh/no_password' will get you on to 127.0.0.1 as davedave
```

To try against a bunch of hosts (the more useful mode):

```
root# python sshfriendfinder.py -H davedave -t host.example.org hosty.example.org 127.0.0.1
Trying against host.example.org:
It broke with [Errno 8] nodename nor servname provided, or not known
Trying against hosty.example.org:
It broke with [Errno 8] nodename nor servname provided, or not known
Trying against 127.0.0.1:
'/Users/davedave/.ssh/no_password' will get you on to 127.0.0.1 as davedave
```

To try against a pattern matched host based on the username
```
root# python sshfriendfinder.py -H davedave -T magicalcloud-%s.aws.example.org
Trying against magicalcloud-davedave.aws.example.org 
'/Users/davedave/.ssh/no_password' will get you on to magicalcloud-davedave.aws.example.org as davedave
```

To search the entire filesystem for any keys (so any RSA keys) and try and SSH around as whoever owns that file.
(this will take a long time as ag has to search every single file under the directory path)

```
root# python sshfriendfinder.py -d /home/
'/home/davedave/.ssh/no_password' will get you on to 127.0.0.1 as davedave
```

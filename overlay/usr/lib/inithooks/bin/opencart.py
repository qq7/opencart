#!/usr/bin/python
"""Set OpenCart admin password, email and domain to serve

Option:
    --pass=     unless provided, will ask interactively
    --email=    unless provided, will ask interactively
    --domain=   unless provided, will ask interactively
        DEFAULT="https://www.example.com"
"""

import os
import re
import sys
import getopt
import inithooks_cache
import time
import hashlib

from dialog_wrapper import Dialog
from mysqlconf import MySQL
from executil import system
from random import randint


def usage(s=None):
    if s:
        print >> sys.stderr, "Error:", s
    print >> sys.stderr, "Syntax: %s [options]" % sys.argv[0]
    print >> sys.stderr, __doc__
    sys.exit(1)


DEFAULT_DOMAIN = "http://example.com/"


def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h",
                                       ['help', 'pass=', 'email=', 'domain='])
    except getopt.GetoptError, e:
        usage(e)

    password = ""
    email = ""
    domain = ""
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt == '--pass':
            password = val
        elif opt == '--email':
            email = val
        elif opt == '--domain':
            domain = val
    if not password:
        d = Dialog('TurnKey Linux - First boot configuration')
        password = d.get_password(
            "OpenCart Password",
            "Enter new password for the OpenCart 'admin' account.")

    if not email:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        email = d.get_email(
            "OpenCart Email",
            "Enter email address for the OpenCart 'admin' account.",
            "admin@example.com")
    inithooks_cache.write('APP_EMAIL', email)
    if not domain:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')
        domain = d.get_input(
                "OpenCart domain",
                "Enter domain to serve OpenCart",
                "example.com")

    if domain == "DEFAULT":
        domain = DEFAULT_DOMAIN

    inithooks_cache.write('APP_DOMAIN', domain)
    
    domain.replace('https://', '')
    domain.replace('http://', '')
    domain.
    
    def php_uniqid(prefix=''):
        return prefix + hex(int(time.time()))[2:10] + hex(int(time.time() * 1000000) % 0x100000)[2:7]

    system("sed -ri \"s|('HTTP(S?)_(SERVER\\|CATALOG)',) '.*/?(admin/)?'|\\1 'http\\L\\2://%s/\\4'|g\" /var/www/opencart/config.php" % domain)
    system("sed -ri \"s|('HTTP(S?)_(SERVER\\|CATALOG)',) '.*/?(admin/)?'|\\1 'http\\L\\2://%s/admin/'|g\" /var/www/opencart/admin/config.php" % domain)
    salt = hashlib.md5(php_uniqid(str(randint(100000000, 999999999)))).hexdigest()[:9]

    password_hash = hashlib.sha1(salt + hashlib.sha1(salt + hashlib.sha1(password).hexdigest()).hexdigest()).hexdigest()

    m = MySQL()
    m.execute('UPDATE opencart.oc_user SET email="%s" WHERE username="admin"' % email)
    m.execute('UPDATE opencart.oc_user SET password="%s" WHERE username="admin"' % password_hash)
    m.execute('UPDATE opencart.oc_user SET salt="%s" WHERE username="admin"' % salt)

if __name__ == "__main__":
    main()

#
# Copyright (c) 2001 Bizar Software Pty Ltd (http://www.bizarsoftware.com.au/)
# This module is free software, and you may redistribute it and/or modify
# under the same terms as Python, so long as this copyright message and
# disclaimer are retained in their original form.
#
# IN NO EVENT SHALL BIZAR SOFTWARE PTY LTD BE LIABLE TO ANY PARTY FOR
# DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING
# OUT OF THE USE OF THIS CODE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# BIZAR SOFTWARE PTY LTD SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE.  THE CODE PROVIDED HEREUNDER IS ON AN "AS IS"
# BASIS, AND THERE IS NO OBLIGATION WHATSOEVER TO PROVIDE MAINTENANCE,
# SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
# 
# $Id: init.py,v 1.18 2001-11-22 15:46:42 jhermann Exp $

__doc__ = """
Init (create) a roundup instance.
"""

import os, sys, errno

import roundup.instance, password
from roundup import install_util

def copytree(src, dst, symlinks=0):
    """Recursively copy a directory tree using copyDigestedFile().

    The destination directory os allowed to exist.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.

    XXX copied from shutil.py in std lib

    """
    names = os.listdir(src)
    try:
        os.mkdir(dst)
    except OSError, error:
        if error.errno != errno.EEXIST: raise
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        if symlinks and os.path.islink(srcname):
            linkto = os.readlink(srcname)
            os.symlink(linkto, dstname)
        elif os.path.isdir(srcname):
            copytree(srcname, dstname, symlinks)
        else:
            install_util.copyDigestedFile(srcname, dstname)

def init(instance_home, template, backend, adminpw):
    '''Initialise an instance using the named template and backend.

    instance_home - the directory to place the instance data in
    template - the template to use in creating the instance data
    backend - the database to use to store the instance data
    adminpw - the password for the "admin" user

    The instance_home directory will be created using the files found in
    the named template (roundup.templates.<name>). A standard instance_home
    contains:
        . instance_config.py
          - simple configuration of things like the email address for the
            mail gateway, the mail domain, the mail host, ...
        . dbinit.py and select_db.py
          - defines the schema for the hyperdatabase and indicates which
            backend to use.
        . interfaces.py
          - defines the CGI Client and mail gateway MailGW classes that are
            used by roundup.cgi, roundup-server and roundup-mailgw.
        . __init__.py
          - ties together all the instance information into one interface
        . db/
          - the actual database that stores the instance's data
        . html/
          - the html templates that are used by the CGI Client
        . detectors/
          - the auditor and reactor modules for this instance

    The html directory is typically extracted from the htmlbase module in
    the template.
    '''
    # first, copy the template dir over
    import roundup.templatebuilder

    template_dir = os.path.split(__file__)[0]
    template_name = template
    template = os.path.join(template_dir, 'templates', template)
    copytree(template, instance_home)

    roundup.templatebuilder.installHtmlBase(template_name, instance_home)

    # now select database
    db = '''# WARNING: DO NOT EDIT THIS FILE!!!
from roundup.backends.back_%s import Database'''%backend
    open(os.path.join(instance_home, 'select_db.py'), 'w').write(db)

    # now import the instance and call its init
    instance = roundup.instance.open(instance_home)
    instance.init(password.Password(adminpw))

#
# $Log: not supported by cvs2svn $
# Revision 1.17  2001/11/12 23:17:38  jhermann
# Code using copyDigestedFile() that passes unit tests
#
# Revision 1.16  2001/10/09 07:25:59  richard
# Added the Password property type. See "pydoc roundup.password" for
# implementation details. Have updated some of the documentation too.
#
# Revision 1.15  2001/08/07 00:24:42  richard
# stupid typo
#
# Revision 1.14  2001/08/07 00:15:51  richard
# Added the copyright/license notice to (nearly) all files at request of
# Bizar Software.
#
# Revision 1.13  2001/08/06 01:20:00  richard
# Added documentaion.
#
# Revision 1.12  2001/08/05 07:43:52  richard
# Instances are now opened by a special function that generates a unique
# module name for the instances on import time.
#
# Revision 1.11  2001/08/04 22:42:43  richard
# Fixed sf.net bug #447671 - typo
#
# Revision 1.10  2001/08/03 01:28:33  richard
# Used the much nicer load_package, pointed out by Steve Majewski.
#
# Revision 1.9  2001/08/03 00:59:34  richard
# Instance import now imports the instance using imp.load_module so that
# we can have instance homes of "roundup" or other existing python package
# names.
#
# Revision 1.8  2001/07/29 07:01:39  richard
# Added vim command to all source so that we don't get no steenkin' tabs :)
#
# Revision 1.7  2001/07/28 07:59:53  richard
# Replaced errno integers with their module values.
# De-tabbed templatebuilder.py
#
# Revision 1.6  2001/07/24 11:18:25  anthonybaxter
# oops. left a print in
#
# Revision 1.5  2001/07/24 10:54:11  anthonybaxter
# oops. Html.
#
# Revision 1.4  2001/07/24 10:46:22  anthonybaxter
# Added templatebuilder module. two functions - one to pack up the html base,
# one to unpack it. Packed up the two standard templates into htmlbases.
# Modified __init__ to install them.
#
# __init__.py magic was needed for the rather high levels of wierd import magic.
# Reducing level of import magic == (good, future)
#
# Revision 1.3  2001/07/23 08:45:28  richard
# ok, so now "./roundup-admin init" will ask questions in an attempt to get a
# workable instance_home set up :)
# _and_ anydbm has had its first test :)
#
# Revision 1.2  2001/07/22 12:09:32  richard
# Final commit of Grande Splite
#
#
# vim: set filetype=python ts=4 sw=4 et si

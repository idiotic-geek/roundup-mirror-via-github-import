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
# $Id: templatebuilder.py,v 1.13.2.1 2002-02-06 04:05:54 richard Exp $
import errno, re

__doc__ = """
Collect template parts and create instance template files.
"""

preamble = """ 
# Do Not Edit (Unless You Want To)
# This file automagically generated by roundup.templatebuilder.makeHtmlBase
# 
"""

def makeHtmlBase(templateDir):
    """ make a htmlbase.py file in the given templateDir, from the
        contents of templateDir/html """
    import os, glob, re
    print "packing up templates in", templateDir
    filelist = glob.glob(os.path.join(templateDir, 'html', '*'))
    filelist = filter(os.path.isfile, filelist) # only want files
    filelist.sort()
    fd = open(os.path.join(templateDir, 'htmlbase.py'), 'w')
    fd.write(preamble)
    for file in filelist:
        # skip the backup files created by richard's vim
        if file[-1] == '~': continue
        mangled_name = os.path.basename(file).replace('.','DOT')
        fd.write('%s = """'%mangled_name)
        fd.write(re.sub(r'\$((Id|File|Log).*?)\$', r'dollar\1dollar',
            open(file).read(), re.I))
        fd.write('"""\n\n')
    fd.close()

def installHtmlBase(template, installDir):
    """ passed a template package and an installDir, unpacks the html files into
      the installdir """
    import os,sys,re

    tdir = __import__('roundup.templates.%s.htmlbase'%template).templates
    if hasattr(tdir, template):
        tmod = getattr(tdir, template)
    else:
        raise "TemplateError", "couldn't find roundup.template.%s.htmlbase"%template
    htmlbase = tmod.htmlbase
    installDir = os.path.join(installDir, 'html')
    try:
        os.makedirs(installDir)
    except OSError, error:
        if error.errno != errno.EEXIST: raise

#    print "installing from", htmlbase.__file__, "into", installDir
    modulecontents = dir(htmlbase)
    for mangledfile in modulecontents:
        if mangledfile[0] == "_": 
            continue
        filename = re.sub('DOT', '.', mangledfile)
        outfile = os.path.join(installDir, filename)
        outfd = open(outfile, 'w')
        data = getattr(htmlbase, mangledfile)
        outfd.write(data)
    


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        makeHtmlBase(sys.argv[1])
    elif len(sys.argv) == 3:
        installHtmlBase(sys.argv[1], sys.argv[2])
    else:
        print "Usage: %s <template directory>"%sys.argv[0]

#
# $Log: not supported by cvs2svn $
# Revision 1.14  2002/02/05 09:59:05  grubert
#  . makeHtmlBase: re.sub under python 2.2 did not replace '.', string.replace does it.
#
# Revision 1.13  2001/11/22 15:46:42  jhermann
# Added module docstrings to all modules.
#
# Revision 1.12  2001/11/14 21:35:21  richard
#  . users may attach files to issues (and support in ext) through the web now
#
# Revision 1.11  2001/08/07 00:24:42  richard
# stupid typo
#
# Revision 1.10  2001/08/07 00:15:51  richard
# Added the copyright/license notice to (nearly) all files at request of
# Bizar Software.
#
# Revision 1.9  2001/08/01 05:06:10  richard
# htmlbase doesn't have extraneous $Foo$ in it any more
#
# Revision 1.8  2001/07/30 08:12:17  richard
# Added time logging and file uploading to the templates.
#
# Revision 1.7  2001/07/30 00:06:52  richard
# Hrm - had IOError instead of OSError. Not sure why there's two. Ho hum.
#
# Revision 1.6  2001/07/29 07:01:39  richard
# Added vim command to all source so that we don't get no steenkin' tabs :)
#
#
#
# vim: set filetype=python ts=4 sw=4 et si

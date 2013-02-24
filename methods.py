#!/usr/bin/env python

from trac import Trac

trac = Trac()

print trac.trac.system.listMethods()

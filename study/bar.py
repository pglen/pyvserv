#!/usr/bin/env python

import foo

print(foo.var2)

print(foo.Config.var)
foo.printconfig()

foo.Config.var = 10
foo.var2 = 11

print(foo.Config.var)
foo.printconfig()

foo.var2 = 3
print(foo.var2)

def chvar():
    foo.var2 = 4
    print(foo.var2)

chvar()
print(foo.var2)
foo.printconfig()


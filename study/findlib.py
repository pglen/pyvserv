
from ctypes.util import find_library
import sys

lll = find_library(sys.argv[1])

print lll

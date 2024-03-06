#!/bin/bash
ps xa | grep "python3 ./pyvserv" | awk '{print $1}' | xargs -i kill {}

#!/usr/bin/env python

import os, sys
import pymisc
import playsound

print("test sound")

#ps = pymisc.PlaySound()
#ps.play("sounds/click.ogg")

sx = pymisc.Soundx()
sx.play_sound("click")
sx.play_sound("click")

#playsound.playsound("sounds/click.ogg")

# EOF

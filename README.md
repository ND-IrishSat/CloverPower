# CloverPower

To view the I2C registers, use the readMPPT.py file. This file prints out the value of the registers to the terminal using the curses library.

1. Power on the pi and wait ~ 30 seconds for the ssh to be available
2. type `ssh cloverPower@10.7.171.93` into terminal
   Note: it's possible that the Pi's ip address could have changed. If this happens, plug the pi into a moniter with an hdmi and use a keyboard to use the command line interface.
   1. Type `cloverPower` into the user and `irishsat` into the password, then type `ifconfig` the ip address will be listed on this screen, then replace the ip in SSH with this new
   address
3. Once you have command line access, type `python3 updateMPPT.py`

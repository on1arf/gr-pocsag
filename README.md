gr-pocsag: a gnuradio embedded python block for sending pocsag messages
-----------------------------------------------------------------------


This is the alpha test release of gr-pocsag, a embedded python block for generating and
sending pocsag message.

The gnu-radio companion example uses a hackRF to send a pocsag-message on 433.900 Mhz.


The block generates the bitpattern for a POCSAG-message, broadcasts it once and then going into a loop
to shut down the transmitter module of the HackRF.


The python code itself is located inside the "pocsag generator" epy_block and as a seperate file "gr-pocsagsend.py".



Release-information:
Version: 0.0.1 (20180826)
Version: 0.0.2 (20180828)


(C) Kristoff Bonne - ON1ARF
This code is released under the GPL v3 license.


Have fun!

73
Kristoff - ON1ARF

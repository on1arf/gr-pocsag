# gr-pocsag: a gnuradio embedded python block for sending pocsag messages

## Description:
This is the alpha test release of gr-pocsag, a embedded python block for generating and
sending pocsag message.

The gnu-radio companion example uses a hackRF to send a pocsag-message

The block generates the bitpattern for a POCSAG-message, broadcasts it once and then going into a loop
to shut down the transmitter module of the HackRF.

The python code itself is located inside the pocsag_generator.py.

## Install:

1. Install GNU Radio like : https://wiki.gnuradio.org/index.php/InstallingGR

2. Install dependencies
```
pip install numpy
pip install bitstring
```

## Usage:

1. By import the pocsagsend.grc in GNU Radio.
2. By call ./pocsag_sender.py --RIC %RIC --SUBRIC %SUBRIC% --TEST %TEXT%  (Please edit frequency in script)

## Release-information:


+ Version: 0.0.1 (20180826)
+ Version: 0.0.2 (20180828)
+ Version: 0.0.3 (20181006) --> 
+ Version: 0.0.4 (20181022) --> Add some Improvments + Changed Parameters and Varaibles + Remove WXGUI




(C) Tauebenuss
(C) Kristoff Bonne - ON1ARF
This code is released under the GPL v3 license.

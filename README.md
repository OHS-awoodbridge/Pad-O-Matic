# Pad-O-Matic

Adapted from the original Pad-O-Matic, modified to:
- use a Mighty Ohm geiger counter to generate randomness https://www.adafruit.com/product/483?srsltid=AfmBOoq4lWzNoEGYWhCjgTloVjrkflij2diQ_T4K3CcCHo9Z24fh1inW
- use CircuitPython in stead of Arduino C++ 



## Geiger Counter click into random numbers
THe method used to create random number is to collect the monotonic time of three clicks (time.monotonic_ns()) if the distance between the first two clicks is greater, it's a 1 otherwise it's a 0. I used this method on my previous Radiant Dice project which showed an even distribution over 800.000 clicks.







  To see the original IEEE Spectrum Hands On article, visit:
  https://spectrum.ieee.org/diy-one-time-pad-machine


# MIDI keypad

I picked up a [midiplus miniEngine MIDI sound module](https://www.amazon.com/dp/B074WYSCF6)
to expand the capabilities of my Yamaha P-115 Digital Piano. Unfortunately, the miniEngine
was difficult to use so I wrote a little program to capture input from a keypad to change
programs and play notes while displaying helpful information on the
[Mini Color PiTFT display](https://www.adafruit.com/product/4475) from Adafruit.

Things that could be improved:
- Allow for two event loops to run asynchronous to also capture display buttons.
- Somehow stifle keypad presses dumping characters into the (unseen) login prompt,
  or just use another 4x4 keypad that connects to the open GPIO pins.
- Instead of using the `NUM LOCK` to play notes (which is not that useful),
  it could be nice to have more programmable preset keys or a simple secuencer
  for recording and playing back bass lines and drum tracks.

![alt text](https://raw.githubusercontent.com/woodie/midi_keypad/main/docs/setup.jpg)

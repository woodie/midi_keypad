# midi_keypad
A little program to capture input from a keypad and change programs on the midi device.

Things that could be improved:
- Use MIDI API to send MIDI commands (instead of dumpling them to the command-line)
- Allow for two event looks to run asynchronous so we can also capture display buttons
- Somehow stifle the keypad from entering characters into the (unseen) login prompt

![alt text](https://raw.githubusercontent.com/woodie/midi_keypad/main/docs/setup.jpg)

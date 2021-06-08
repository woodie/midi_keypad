import os
import string

from evdev import InputDevice
from select import select

dev = InputDevice('/dev/input/by-id/usb-04d9_1203-event-kbd')
keys = dict([(69, 'N'), (98, '/'), (55, '*'), (14, 'B'),
             (71, '7'), (72, '8'), (73, '9'), (74, '-'),
             (75, '4'), (76, '5'), (77, '6'), (78, '+'),
             (79, '1'), (80, '2'), (81, '3'),
             (82, '0'), (83, '.'), (96, 'E')])

notes = [59, 60, 62, 64, 65, 67, 69, 71, 72, 74]

presets = {'.': 62, # Synth Bass 1
           '/': 53, # Voice Oohs
           '*': 81} # Lead Synth (sawtooth)

try:
  tty = os.open('/dev/tty0', os.O_RDWR)
except:
  tty = None

number_lock = 0 
program_num = 5 
accumulator = ''

def change_program(num):
  fmt = "{0:x}".format(num)
  os.system('amidi -p hw:1,0,0 -S "C0 %s"' % fmt)

def send_midi_note(num):
  fmt = "{0:x}".format(num)
  os.system('amidi -p hw:1,0,0 -S "90 %s 7F"' % fmt)
  os.system('amidi -p hw:1,0,0 -S "90 %s 00"' % fmt)

while True:
   r,w,x = select([dev], [], []) 
   for event in dev.read():
       if event.type == 1 and event.value == 1 and event.code in keys:
         if keys[event.code] in '0123456789':
           if number_lock == 1:
             send_midi_note(notes[int(keys[event.code])])
           else:
             accumulator += keys[event.code]
         elif keys[event.code] in './*':
           program_num = presets[keys[event.code]]
           change_program(program_num)
         elif keys[event.code] == 'B' and accumulator != '': 
           accumulator = accumulator[:-1]
         elif keys[event.code] == 'E' and accumulator != '': 
           program_num = int(accumulator) % 128 
           accumulator = ''
           change_program(program_num)
         elif keys[event.code] == '-':
           program_num = 127 if program_num <= 0 else program_num - 1 
           change_program(program_num)
         elif keys[event.code] == '+':
           program_num = 0 if program_num >= 127 else program_num + 1 
           change_program(program_num)
         if tty:
           os.write(tty, '\b')
       elif event.type == 17 and event.code == 0:
         number_lock = event.value

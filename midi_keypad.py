#import asyncio
import board
import digitalio
import os
import string
import time
import adafruit_rgb_display.st7789 as st7789

from evdev import InputDevice
from select import select
from PIL import Image, ImageDraw, ImageFont
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON, PROGRAM_CHANGE

midiout, port_name = open_midioutput(1)

text_file = open('/usr/share/midi/programs.txt', 'r')
programs = text_file.read().split('\n')
text_file.close()

disp = st7789.ST7789( board.SPI(),
    cs=digitalio.DigitalInOut(board.CE0),
    dc=digitalio.DigitalInOut(board.D25),
    rst=None, baudrate=64000000,
    width=135, height=240,
    x_offset=53, y_offset=40,
)

image = Image.new('RGB', (disp.height, disp.width))
draw = ImageDraw.Draw(image)
gt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 66)
lg = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 44)
sm = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 30)
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

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

number_lock = 0
program_num = 0
accumulator = ''

def line_break(label):
  parts = label.split()[1:]
  if len(parts) < 2:
    return [parts[0], '']
  if ' (' in label:
    pair = ' '.join(parts).split(' (')
    return [pair[0], '(' + pair[1]]
  else:
    return [parts[0], ' '.join(parts[1:])]

def change_program(num):
  draw.rectangle((0, 0, disp.height, disp.width), outline=0, fill=0)
  lines = line_break(programs[num])
  draw.text((0, 8), 'Program:', font=sm, fill="#FFFFFF")
  draw.text((160, -2), str(num), font=lg, fill="#FFFFFF")
  draw.text((0, 50), lines[0], font=sm, fill="#00FF00")
  draw.text((0, 90), lines[1], font=sm, fill="#00FF00")
  disp.image(image, 270)
  midiout.send_message([PROGRAM_CHANGE, num])

def build_patch(num):
  draw.rectangle((0, 0, disp.height, disp.width), outline=0, fill=0)
  draw.text((0, 8), 'Program:', font=sm, fill="#FFFFFF")
  draw.text((0, 50), str(num), font=gt, fill="#FFFF00")
  disp.image(image, 270)

def send_midi_note(num):
  midiout.send_message([NOTE_ON, num, 112])
  time.sleep(0.1)
  midiout.send_message([NOTE_OFF, num, 0])

def shutdown_now():
  draw.rectangle((0, 0, disp.height, disp.width), outline=0, fill=0)
  draw.text((0, 8), 'Shutdown...', font=sm, fill="#FFFF00")
  disp.image(image, 270)
  os.system('shutdown now')

change_program(program_num)

# async def button_presses():
if False:
  while True:
    if buttonB.value and not buttonA.value:  # just button A pressed
      program_num = 0 if program_num >= 127 else program_num + 1
      change_program(program_num)
    if buttonA.value and not buttonB.value:  # just button B pressed
      program_num = 127 if program_num <= 0 else program_num - 1
      change_program(program_num)

if True:
  while True:
    r,w,x = select([dev], [], [])
    for event in dev.read():
      if event.type == 1 and event.value == 1 and event.code in keys:
        if keys[event.code] in '0123456789':
          if number_lock == 1:
            send_midi_note(notes[int(keys[event.code])])
          else:
            accumulator += keys[event.code]
            build_patch(accumulator)
        elif keys[event.code] in './*':
          program_num = presets[keys[event.code]]
          change_program(program_num)
        elif keys[event.code] == 'B' and accumulator != '':
          accumulator = accumulator[:-1]
          build_patch(accumulator)
        elif keys[event.code] == 'E' and accumulator != '':
          if accumulator == '911':
            del midiout
            shutdown_now()
            exit()
          else:
            program_num = int(accumulator) % 128
            accumulator = ''
            change_program(program_num)
        elif keys[event.code] == '-':
          program_num = 127 if program_num <= 0 else program_num - 1
          change_program(program_num)
        elif keys[event.code] == '+':
          program_num = 0 if program_num >= 127 else program_num + 1
          change_program(program_num)
      elif event.type == 17 and event.code == 0:
        number_lock = event.value

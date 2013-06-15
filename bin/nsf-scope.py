#!/usr/bin/env python

import sys
import os
import os.path
import argparse
import bread as b

ARGS = None

def error(msg):
  sys.stderr.write('error: %s\n' % msg)
  sys.exit(1)

def basename(path):
  fn = os.path.basename(path)
  bn = os.path.splitext(fn)[0]
  return bn

def ensuredir(d):
  if os.path.exists(d):
    if os.path.isdir(d):
      return # everything ok
    else:
      error('"%s" exists, but is not a directory' % d)
  else:
    os.makedirs(d)

def logF(path, x):
  if ARGS.log:
    ensuredir(os.path.dirname(path))
    with open(path, 'w') as f:
      f.write(x)

def hex_array(x):
  return str(map(hex, x))

nsf_head_spec = \
  [ ('magic_number', b.array(5, b.byte), {"str_format": hex_array})
  , ('version', b.byte)
  , ('total_songs', b.byte)
  , ('starting_song', b.byte)
  , ('load_addr', b.uint16, {"str_format": hex})
  , ('init_addr', b.uint16, {"str_format": hex})
  , ('play_addr', b.uint16, {"str_format": hex})
  , ('title', b.string(32))
  , ('artist', b.string(32))
  , ('copyright', b.string(32))
  , ('ntsc_speed', b.uint16)
  , ('bankswitch_init', b.array(8, b.byte), {"str_format": hex_array})
  , ('pal_speed', b.uint16)
  , ('tv_std', b.boolean, {"str_format": lambda x: "PAL" if x else "NTSC"})
  , ('ntsc_and_pal', b.boolean)
  , (b.padding(6))
  , ('vrc6', b.boolean)
  , ('vrc7', b.boolean)
  , ('fds', b.boolean)
  , ('mmc5', b.boolean)
  , ('namco_106', b.boolean)
  , ('fme07', b.boolean)
  , (b.padding(2))
  , (b.padding(32))
  ]

def scopetune(path):
  name = basename(path)
  with open(path, 'r') as f:
    bin_head = f.read(128)
    bin_code = f.read()
  head = b.parse(bin_head, nsf_head_spec)
  head.add_key('code_size', len(bin_code))
  head.add_key('name', name)

  if ARGS.log:
    tlog = os.path.join(ARGS.log, name)
    logF(os.path.join(tlog, 'head.bin'), bin_head)
    logF(os.path.join(tlog, 'code.bin'), bin_code)
    logF(os.path.join(tlog, 'head.txt'), str(head))
    # TODO disassemble code.bin

  return head

def main():
  global ARGS
  ap = argparse.ArgumentParser(description='Analyze NSF chiptues.')
  ap.add_argument('tunes', metavar='tune', nargs='+',
                  help='tune file to analyze')
  ap.add_argument('-l', '--log',
                  help='log intermediate steps in LOG/')
  ARGS = ap.parse_args()

  props = [ scopetune(t) for t in ARGS.tunes ]
  # TODO csv props

if __name__ == '__main__':
  main()

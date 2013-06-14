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

def mkdir(d):
  if os.path.exists(d):
    if ARGS.force:
      if os.path.isdir(d):
        pass # everything ok
      else:
        error('"%s" is not a directory' % d)
    else:
      error('"%s" already exists, to overwrite use --force' % d)
  else:
    os.makedirs(d)

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
  tout = os.path.join(ARGS.out, name)
  mkdir(tout)

  with open(path, 'r') as f:
    bin_head = f.read(128)
    bin_code = f.read()

  with open(os.path.join(tout, 'head.bin'), 'w') as f:
    f.write(bin_head)
  with open(os.path.join(tout, 'code.bin'), 'w') as f:
    f.write(bin_code)

  head = b.parse(bin_head, nsf_head_spec)
  with open(os.path.join(tout, 'head.txt'), 'w') as f:
    f.write(str(head))
    f.write('# extras\n')
    f.write('code_size: %d\n' % len(bin_code))
    f.write('last_code_addr: 0x%x\n' % (head.load_addr + len(bin_code) - 1))

def main():
  global ARGS
  ap = argparse.ArgumentParser(description='Analyze NSF chiptues.')
  ap.add_argument('tunes', metavar='tune', nargs='+',
                  help='tune file to analyze')
  ap.add_argument('-o', '--out', default='nsf-scope-out',
                  help='place results in OUT/')
  ap.add_argument('-f', '--force', action='store_true',
                  help='overwrite any previous results')
  ARGS = ap.parse_args()

  mkdir(ARGS.out)
  for t in ARGS.tunes:
    scopetune(t)

if __name__ == '__main__':
  main()

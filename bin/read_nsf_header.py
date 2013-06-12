#!/usr/bin/env python

import bread as b
import py65.monitor as py65
import sys

def hex_array(x):
  return str(map(hex, x))

hdr_spec = \
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

def disasm(bin, load_addr):
  # this is an ungodly hack, user must hit enter twice :\
  m = py65.Monitor()
  m._output = lambda _: ()
  m._fill(load_addr, load_addr, bin)
  code = []
  m._output = lambda i: code.append(i)
  m.do_disassemble('%x:%x' % (load_addr, load_addr + len(bin) - 1))
  return '\n'.join(code)

class NSF:
  def __init__(self, path):
    with open(path, 'r') as f:
      hdr = f.read(128)
      bin = map(ord, f.read())
    self.hdr = b.parse(hdr, hdr_spec)

    # ensure binary will fit in address space
    max_sz = 0x10000 - self.hdr.load_addr
    if len(bin) > max_sz:
      bin = bin[:max_sz]

    self.asm = disasm(bin, self.hdr.load_addr)

def main():
  nsf = NSF(sys.argv[1])
  print nsf.hdr
  print nsf.asm

if __name__ == "__main__":
  main()

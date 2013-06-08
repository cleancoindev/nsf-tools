#!/usr/bin/env python

import bread as b
import sys

class NSF:
  def hex_array(x):
    return str(map(hex, x))

  hdr_spec = [
    ('magic_number', b.array(5, b.byte), {"str_format": hex_array}),
    ('version', b.byte),
    ('total_songs', b.byte),
    ('starting_song', b.byte),
    ('load_addr', b.uint16, {"str_format": hex}),
    ('init_addr', b.uint16, {"str_format": hex}),
    ('play_addr', b.uint16, {"str_format": hex}),
    ('title', b.string(32)),
    ('artist', b.string(32)),
    ('copyright', b.string(32)),
    ('ntsc_speed', b.uint16),
    ('bankswitch_init', b.array(8, b.byte), {"str_format": hex_array}),
    ('pal_speed', b.uint16),
    ('tv_std', b.boolean, {"str_format": lambda x: "PAL" if x else "NTSC"}),
    ('ntsc_and_pal', b.boolean),
    (b.padding(6)),
    ('vrc6', b.boolean),
    ('vrc7', b.boolean),
    ('fds', b.boolean),
    ('mmc5', b.boolean),
    ('namco_106', b.boolean),
    ('fme07', b.boolean),
    (b.padding(2)),
    (b.padding(32))
  ]

  def __init__(self, path):
    with open(path, 'r') as f:
      d = f.read()
    self.path = path
    self.hdr  = b.parse(d[0:128], NSF.hdr_spec)
    self.code = d[128:]

def main():
  print NSF(sys.argv[1]).hdr

if __name__ == "__main__":
  main()

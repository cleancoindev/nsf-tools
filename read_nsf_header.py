#!/usr/bin/env python

import bread as b
import sys

def hex_array(x):
    return str(map(hex, x))

nsf_header = [
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
    ('ntsc', b.boolean),
    ('pal', b.boolean),
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

def main():
  with open(sys.argv[1], 'r') as fp:
      header = b.parse(fp, nsf_header)
      print header

if __name__ == "__main__":
  main()

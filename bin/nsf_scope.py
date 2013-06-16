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

def warn(msg):
  sys.stderr.write('warn: %s\n' % msg)

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

class Instr:
  def __init__(self, op, amode, opand, size):
    self.op    = op
    self.amode = amode
    self.opand = opand
    self.size  = size

  def __str__(self):
    if self.size == 1:
      a = ''
    elif self.size == 2:
      a = '0x%02x' % self.opand
    elif self.size == 3:
      a = '0x%04x' % self.opand
    else:
      error('bad instr size %d' % self.size)
    return '%-3s (%-4s) %s' % (self.op, self.amode, a)

# http://www.6502.org/tutorials/6502opcodes.html
disasm_tab = \
  { 0x69: ('ADC', 'IMM',  2)
  , 0x65: ('ADC', 'ZP',   2)
  , 0x75: ('ADC', 'ZPX',  2)
  , 0x6D: ('ADC', 'ABS',  3)
  , 0x7D: ('ADC', 'ABSX', 3)
  , 0x79: ('ADC', 'ABSY', 3)
  , 0x61: ('ADC', 'INDX', 2)
  , 0x71: ('ADC', 'INDY', 2)
  , 0x29: ('AND', 'IMM',  2)
  , 0x25: ('AND', 'ZP',   2)
  , 0x35: ('AND', 'ZPX',  2)
  , 0x2D: ('AND', 'ABS',  3)
  , 0x3D: ('AND', 'ABSX', 3)
  , 0x39: ('AND', 'ABSY', 3)
  , 0x21: ('AND', 'INDX', 2)
  , 0x31: ('AND', 'INDY', 2)
  , 0x0A: ('ASL', 'ACC',  1)
  , 0x06: ('ASL', 'ZP',   2)
  , 0x16: ('ASL', 'ZPX',  2)
  , 0x0E: ('ASL', 'ABS',  3)
  , 0x1E: ('ASL', 'ABSX', 3)
  , 0x24: ('BIT', 'ZP',   2)
  , 0x2C: ('BIT', 'ABS',  3)
  , 0x00: ('BRK', 'IMP',  1)
  , 0xC9: ('CMP', 'IMM',  2)
  , 0xC5: ('CMP', 'ZP',   2)
  , 0xD5: ('CMP', 'ZPX',  2)
  , 0xCD: ('CMP', 'ABS',  3)
  , 0xDD: ('CMP', 'ABSX', 3)
  , 0xD9: ('CMP', 'ABSY', 3)
  , 0xC1: ('CMP', 'INDX', 2)
  , 0xD1: ('CMP', 'INDY', 2)
  , 0xE0: ('CPX', 'IMM',  2)
  , 0xE4: ('CPX', 'ZP',   2)
  , 0xEC: ('CPX', 'ABS',  3)
  , 0xC0: ('CPY', 'IMM',  2)
  , 0xC4: ('CPY', 'ZP',   2)
  , 0xCC: ('CPY', 'ABS',  3)
  , 0xC6: ('DEC', 'ZP',   2)
  , 0xD6: ('DEC', 'ZPX',  2)
  , 0xCE: ('DEC', 'ABS',  3)
  , 0xDE: ('DEC', 'ABSX', 3)
  , 0x49: ('EOR', 'IMM',  2)
  , 0x45: ('EOR', 'ZP',   2)
  , 0x55: ('EOR', 'ZPX',  2)
  , 0x4D: ('EOR', 'ABS',  3)
  , 0x5D: ('EOR', 'ABSX', 3)
  , 0x59: ('EOR', 'ABSY', 3)
  , 0x41: ('EOR', 'INDX', 2)
  , 0x51: ('EOR', 'INDY', 2)
  , 0xE6: ('INC', 'ZP',   2)
  , 0xF6: ('INC', 'ZPX',  2)
  , 0xEE: ('INC', 'ABS',  3)
  , 0xFE: ('INC', 'ABSX', 3)
  , 0x4C: ('JMP', 'ABS',  3)
  , 0x6C: ('JMP', 'IND',  3)
  , 0x20: ('JSR', 'ABS',  3)
  , 0xA9: ('LDA', 'IMM',  2)
  , 0xA5: ('LDA', 'ZP',   2)
  , 0xB5: ('LDA', 'ZPX',  2)
  , 0xAD: ('LDA', 'ABS',  3)
  , 0xBD: ('LDA', 'ABSX', 3)
  , 0xB9: ('LDA', 'ABSY', 3)
  , 0xA1: ('LDA', 'INDX', 2)
  , 0xB1: ('LDA', 'INDY', 2)
  , 0xA2: ('LDX', 'IMM',  2)
  , 0xA6: ('LDX', 'ZP',   2)
  , 0xB6: ('LDX', 'ZPY',  2)
  , 0xAE: ('LDX', 'ABS',  3)
  , 0xBE: ('LDX', 'ABSY', 3)
  , 0xA0: ('LDY', 'IMM',  2)
  , 0xA4: ('LDY', 'ZP',   2)
  , 0xB4: ('LDY', 'ZPX',  2)
  , 0xAC: ('LDY', 'ABS',  3)
  , 0xBC: ('LDY', 'ABSX', 3)
  , 0x4A: ('LSR', 'ACC',  1)
  , 0x46: ('LSR', 'ZP',   2)
  , 0x56: ('LSR', 'ZPX',  2)
  , 0x4E: ('LSR', 'ABS',  3)
  , 0x5E: ('LSR', 'ABSX', 3)
  , 0xEA: ('NOP', 'IMP',  1)
  , 0x09: ('ORA', 'IMM',  2)
  , 0x05: ('ORA', 'ZP',   2)
  , 0x15: ('ORA', 'ZPX',  2)
  , 0x0D: ('ORA', 'ABS',  3)
  , 0x1D: ('ORA', 'ABSX', 3)
  , 0x19: ('ORA', 'ABSY', 3)
  , 0x01: ('ORA', 'INDX', 2)
  , 0x11: ('ORA', 'INDY', 2)
  , 0x2A: ('ROL', 'ACC',  1)
  , 0x26: ('ROL', 'ZP',   2)
  , 0x36: ('ROL', 'ZPX',  2)
  , 0x2E: ('ROL', 'ABS',  3)
  , 0x3E: ('ROL', 'ABSX', 3)
  , 0x6A: ('ROR', 'ACC',  1)
  , 0x66: ('ROR', 'ZP',   2)
  , 0x76: ('ROR', 'ZPX',  2)
  , 0x6E: ('ROR', 'ABS',  3)
  , 0x7E: ('ROR', 'ABSX', 3)
  , 0x40: ('RTI', 'IMP',  1)
  , 0x60: ('RTS', 'IMP',  1)
  , 0xE9: ('SBC', 'IMM',  2)
  , 0xE5: ('SBC', 'ZP',   2)
  , 0xF5: ('SBC', 'ZPX',  2)
  , 0xED: ('SBC', 'ABS',  3)
  , 0xFD: ('SBC', 'ABSX', 3)
  , 0xF9: ('SBC', 'ABSY', 3)
  , 0xE1: ('SBC', 'INDX', 2)
  , 0xF1: ('SBC', 'INDY', 2)
  , 0x85: ('STA', 'ZP',   2)
  , 0x95: ('STA', 'ZPX',  2)
  , 0x8D: ('STA', 'ABS',  3)
  , 0x9D: ('STA', 'ABSX', 3)
  , 0x99: ('STA', 'ABSY', 3)
  , 0x81: ('STA', 'INDX', 2)
  , 0x91: ('STA', 'INDY', 2)
  , 0x86: ('STX', 'ZP',   2)
  , 0x96: ('STX', 'ZPY',  2)
  , 0x8E: ('STX', 'ABS',  3)
  , 0x84: ('STY', 'ZP',   2)
  , 0x94: ('STY', 'ZPX',  2)
  , 0x8C: ('STY', 'ABS',  3)
  , 0xAA: ('TAX', 'IMP',  1)
  , 0x8A: ('TXA', 'IMP',  1)
  , 0xCA: ('DEX', 'IMP',  1)
  , 0xE8: ('INX', 'IMP',  1)
  , 0xA8: ('TAY', 'IMP',  1)
  , 0x98: ('TYA', 'IMP',  1)
  , 0x88: ('DEY', 'IMP',  1)
  , 0xC8: ('INY', 'IMP',  1)
  , 0x9A: ('TXS', 'IMP',  1)
  , 0xBA: ('TSX', 'IMP',  1)
  , 0x48: ('PHA', 'IMP',  1)
  , 0x68: ('PLA', 'IMP',  1)
  , 0x08: ('PHP', 'IMP',  1)
  , 0x28: ('PLP', 'IMP',  1)
  , 0x18: ('CLC', 'IMP',  1)
  , 0x38: ('SEC', 'IMP',  1)
  , 0x58: ('CLI', 'IMP',  1)
  , 0x78: ('SEI', 'IMP',  1)
  , 0xB8: ('CLV', 'IMP',  1)
  , 0xD8: ('CLD', 'IMP',  1)
  , 0xF8: ('SED', 'IMP',  1)
  , 0x10: ('BPL', 'REL',  2)
  , 0x30: ('BMI', 'REL',  2)
  , 0x50: ('BVC', 'REL',  2)
  , 0x70: ('BVS', 'REL',  2)
  , 0x90: ('BCC', 'REL',  2)
  , 0xB0: ('BCS', 'REL',  2)
  , 0xD0: ('BNE', 'REL',  2)
  , 0xF0: ('BEQ', 'REL',  2)
  }

def disasm(mem, lo=0, hi=None):
  if hi == None:
    hi = len(mem)
  instrs = []
  while lo < hi:
    try:
      op, amode, size = disasm_tab[mem[lo]]
    except KeyError:
      op, amode, size = '???', '???', 1
    if size == 1:
      opand = None
    elif size == 2:
      opand = mem[lo+1]
    elif size == 3:
      opand = (mem[lo+2] << 8) | mem[lo+1]
    else:
      error('bad instr size %d' % self.size)
    instrs.append(Instr(op, amode, opand, size))
    lo += size
  return instrs

class NSF:
  def __init__(self, name, head, code):
    self.name = name
    self.head = head
    self.code = code

def scopetune(path):
  name = basename(path)
  with open(path, 'r') as f:
    bin_head = f.read(128)
    bin_code = f.read()
  head = b.parse(bin_head, nsf_head_spec)
  code = disasm(map(ord, bin_code))

  if ARGS.log:
    tlog = os.path.join(ARGS.log, name)
    logF(os.path.join(tlog, 'head.bin'), bin_head)
    logF(os.path.join(tlog, 'code.bin'), bin_code)
    logF(os.path.join(tlog, 'head.txt'), str(head))
    logF(os.path.join(tlog, 'code.asm'), '\n'.join([str(i) for i in code]))

  return NSF(name, head, code)

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

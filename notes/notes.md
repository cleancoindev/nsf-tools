# Notes on NSF, 6502, etc.

## [NSF Spec](http://kevtris.org/nes/nsfspec.txt)

NSF is basically just raw sound data (music / sound code) with a small
header.  The music can be played using a
[6502](ihttp://en.wikipedia.org/wiki/MOS_Technology_6502) emulator: load
the data into the right part of the address space, initialize, and run.
The header format:

| Offset | Length | Type   | Meaning                                            |
| ------ | ------ | ------ | -------------------------------------------------- |
| 0000   | 5      | STRING | "NESM\x1a" = 4e 45 53 4d 1a                        |
| 0005   | 1      | BYTE   | version number (currently 01h)                     |
| 0006   | 1      | BYTE   | total number of songs                              |
| 0007   | 1      | BYTE   | starting song                                      |
| 0008   | 2      | WORD   | (lo/hi) load address of data (8000-FFFF)           |
| 000a   | 2      | WORD   | (lo/hi) init address of data (8000-FFFF)           |
| 000c   | 2      | WORD   | (lo/hi) play address of data (8000-FFFF)           |
| 000e   | 32     | STRING | song title                                         |
| 002e   | 32     | STRING | artist name                                        |
| 004e   | 32     | STRING | copyright holder                                   |
| 006e   | 2      | WORD   | (lo/hi) NTSC speed (see text)                      |
| 0070   | 8      | BYTE   | bankswitch init values (see text, and FDS section) |
| 0078   | 2      | WORD   | (lo/hi) PAL speed (see text)                       |
| 007a   | 1      | BYTE   | PAL/NTSC bits:                                     |
|        |        |        |   bit 0    : if clear, this is an NTSC tune        |
|        |        |        |   bit 0    : if set, this is a PAL tune            |
|        |        |        |   bit 1    : if set, this is a dual PAL/NTSC tune  |
|        |        |        |   bits 2-7 : not used, *must* be 0                 |
| 007b   | 1      | BYTE   | Extra Sound Chip Support                           |
|        |        |        |   bit 0    : if set, this song uses VRCVI          |
|        |        |        |   bit 1    : if set, this song uses VRCVII         |
|        |        |        |   bit 2    : if set, this song uses FDS Sound      |
|        |        |        |   bit 3    : if set, this song uses MMC5 audio     |
|        |        |        |   bit 4    : if set, this song uses Namco 106      |
|        |        |        |   bit 5    : if set, this song uses Sunsoft FME-07 |
|        |        |        |   bits 6-7 : future expansion, *must* be 0         |
| 007c   | 4      | ----   | 4 extra bytes for expansion (must be 00h)          |
| 0080   | nnn    | ----   | music program/data follows                         |

BYTES are 8 bits and WORDS are 2 BYTES.

Song, artist, and copyright STRINGs are null terminated.

NTSC and PAL speed are in 1/1000000th sec ticks.

We can examine the first 256 bytes of `Tetris.nsf` for an example header:

```
$ xxd -cols 8 Tetrix.nsf | head -n 17
0000000: 4e45 534d 1a01 1f01  NESM....
0000008: 0080 0080 00e0 5465  ......Te
0000010: 7472 6973 0000 0000  tris....
0000018: 0000 0000 0000 0000  ........
0000020: 0000 0000 0000 0000  ........
0000028: 0000 0000 0000 3c3f  ......<?
0000030: 3e00 0000 0000 0000  >.......
0000038: 0000 0000 0000 0000  ........
0000040: 0000 0000 0000 0000  ........
0000048: 0000 0000 0000 3139  ......19
0000050: 3839 204e 696e 7465  89 Ninte
0000058: 6e64 6f00 0000 0000  ndo.....
0000060: 0000 0000 0000 0000  ........
0000068: 0000 0000 0000 1a41  .......A
0000070: 0000 0000 0000 0000  ........
0000078: 0000 0000 0000 0000  ........
0000080: 4820 06e0 2003 e068  H .. ..h
```

Interpretting the values:

| Offset | Length | Content        | Meaning                                    |
| ------ | ------ | -------------- | ------------------------------------------ |
| 00     | 5      | 4e 45 53 4d 1a | "NESM\x1a", denotes NES sound format file  |
| 05     | 1      | 01             | 1, version number                          |
| 06     | 1      | 1f             | 57, total number of songs                  |
| 07     | 1      | 01             | 1, starting song                           |
| 08     | 2      | 00 80          | 0x8000, load address                       |
| 0a     | 2      | 00 80          | 0x8000, init address                       |
| 0c     | 2      | 00 e0          | 0xe000, play address                       |
| 0e     | 32     | 54 65 74 72    | "Tetris", song title                       |
|        |        | 69 73 00 00    |                                            |
|        |        | 00 00 00 00    |                                            |
|        |        | 00 00 00 00    |                                            |
|        |        | 00 00 00 00    |                                            |
|        |        | 00 00 00 00    |                                            |
|        |        | 00 00 00 00    |                                            |
|        |        | 00 00 00 00    |                                            |
| 2e     | 32     | 3c 3f 3e 00    | "<?=", artist name                         |
|        |        | 00 00 00 00    |                                            |
|        |        | 00 00 00 00    |                                            |
|        |        | 00 00 00 00    |                                            |
|        |        | 00 00 00 00    |                                            |
|        |        | 00 00 00 00    |                                            |
|        |        | 00 00 00 00    |                                            |
|        |        | 00 00 00 00    |                                            |
| 4e     | 32     | 31 39 38 39    | "1989 Nintendo", copyright holder          |
|        |        | 20 4e 69 6e    |                                            |
|        |        | 74 65 6e 64    |                                            |
|        |        | 6f 00 00 00    |                                            |
|        |        | 00 00 00 00    |                                            |
|        |        | 00 00 00 00    |                                            |
|        |        | 00 00 00 00    |                                            |
|        |        | 00 00 00 00    |                                            |
| 6e     | 2      | 1a 41          | 0x411a = 16666, NTSC speed                 |
| 70     | 8      | 00 00 00 00    | 0, bank switch values                      |
|        |        | 00 00 00 00    |                                            |
| 78     | 2      | 00 00          | 0, PAL speed                               |
| 7a     | 1      | 00             | 00000000b, NTSC tune                       |
| 7b     | 1      | 00             | 00000000b, no extra sound chips            |
| 7c     | 4      | 00 00 00 00    | 0, expansion bytes                         |
| 80     | ...    | ...            | begin music data                           |

Apparently this header format was inspired by the [PSID
format](http://cpansearch.perl.org/src/LALA/Audio-SID-3.11/SID_file_format.txt) for
[Commodore 64](http://en.wikipedia.org/wiki/Commodore_64) (C64) for C64 music / sound.

### Loading a Tune

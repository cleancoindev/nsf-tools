# Analyze NES Sound Files

Very experimental and hacky tools to pick out interesting features of
chiptunes.

## INSTALL

After cloning, point the `NSF_TOOLS` environment variable to the repo:

```sh
$ git clone https://github.com/ztatlock/nsf-tools.git
$ cd nsf-tools
$ echo "export NSF_TOOLS=$(pwd)" >> ~/.bashrc
$ cd ..
```

NSF Tools also depend on [bread](https://github.com/alexras/bread) and
[py65](https://github.com/mnaberez/py65):

```sh
$ git clone https://github.com/alexras/bread.git
$ echo "export PYTHONPATH=$(pwd)/bread/bread:$PYTHONPATH" >> ~/.bashrc
$ pip insall py65
```

## References

[NES Music Format Spec](http://kevtris.org/nes/nsfspec.txt)

[NES Sound Format](http://en.wikipedia.org/wiki/NES_Sound_Format)

[nullsleep MCK/MML Guide](http://www.nullsleep.com/treasure/mck_guide/)

[6502 Resources](http://www.6502.org/)

NSFs in samples/ from [Zophar's Domain](http://www.zophar.net/music/nsf.html)

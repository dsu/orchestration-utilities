import sys, os
import struct


def get_class_version(patch):
    '''
    https://en.wikipedia.org/wiki/Java_class_file#General_layout
    '''
    majorversions = {"0x34": "1.8", "0x33": "1.7",
                     "0x32": "1.6", "0x31": "1.5", "0x30": "1.4", "0x2F": "1.3", "0x2E": "1.2", "0x2D": "1.1", }
    magicnumber = '0xcafebabe'
    with open(patch, 'rb') as f:
        str = struct.unpack('>IHH', f.read(8))  # big-endian
        # alternatively codecs.getencoder('hex_codec')(f.read(4))[0]
        magic = hex(str[0])
        minor = hex(str[1])
        major = hex(str[2]);
        if (magicnumber == magic):
            # print('ok')
            # print(minor)
            # print(major)
            return majorversions[major];
        else:
            raise Exception('Not a valid class file', patch)


if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
   pass

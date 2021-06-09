#!/usr/bin/env python3

import argparse
import hashlib
import uuid
from logging import debug
from logging.config import dictConfig

import numpy
from PIL import Image
import binascii, struct


class Anon:
    def __init__(self):
        self.salt = uuid.uuid4().hex.encode('utf-8')
        debug("salt: {}".format(self.salt))

    def pseudonym(self, name):
        hashed_name = hashlib.pbkdf2_hmac('sha256', name.encode(), self.salt, 100000)
        # return hashlib.sha512(name.encode('utf-8') + self.salt.encode('utf-8')).hexdigest()
        # hashed_name = binascii.b2a_base64(struct.pack('i', hash(name)))
        return hashed_name


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Vasolabs Controller.",argument_default='start')
    parser.add_argument('-cfgfile', default='controller.ini', help='Use specified file for configuration.')
    parser.add_argument('-imagefile', default='image.bmp', help='Use specified image file.')
    parser.add_argument('action', nargs="?", choices=['start', 'stop', 'restart'], help='Perform the specified action.')
    args = parser.parse_args()
    print(args)



    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] [%(levelname)s] [%(filename)s(%(lineno)d)] [PID:%(process)d]: %(message)s',
            }
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'maxBytes': 100000000,
                'backupCount': 5,
                'filename': '0.anoymize.log',
                'mode': 'w',
            },
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['file']
        }
    })

    debug('first debug: {}'.format(5))
    anon = Anon()
    pseudonym = anon.pseudonym("foozeball")
    debug("pseudonym: {}".format(pseudonym))

    # daemon = ControllerDaemon(args)
    if 'start' == args.action:
        debug('second debug: {}'.format(5))
        im = Image.open(args.imagefile)
        # im.show()
        a = numpy.array(im)
        a = numpy.delete(a, slice(20), axis=0)
        im = Image.fromarray(a)
        # im.show()
        im.save('output.bmp')

    # elif 'stop' == args.action:
    #     daemon.stop()
    # elif 'restart' == args.action:
    #     daemon.restart()
    # else:
    #     raise ValueError('unsupported action: {}'.format(args.action))

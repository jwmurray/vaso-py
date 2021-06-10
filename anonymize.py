#!/usr/bin/env python3

import argparse
import hashlib
import uuid
from os import makedirs, path
import os
from logging import debug
from logging.config import dictConfig

import numpy
from PIL import Image
import binascii, struct


class Anon:
    def __init__(self):
        self.salt = uuid.uuid4().hex.encode('utf-8')
        self.patient_id = 1
        debug("salt: {}".format(self.salt))

    # Create an anonymous
    def pseudonym(self, name):
        hashed_name = hashlib.pbkdf2_hmac('sha256', name.encode(), self.salt, 100000)
        # return hashlib.sha512(name.encode('utf-8') + self.salt.encode('utf-8')).hexdigest()
        # hashed_name = binascii.b2a_base64(struct.pack('i', hash(name)))
        return hashed_name

    # Create anonymous .bmp file from .bmp file
    def anonymize_file(self, input_file_path, output_file_path):
        debug('Anonymizing:  {} ==> {}'.format(input_file_path, output_file_path))
        try:
            input_image = Image.open(input_file_path)
        except:
            return
        a = numpy.array(input_image)
        a = numpy.delete(a, slice(20), axis=0)
        output_image = Image.fromarray(a)
        try:
            output_image.save(output_file_path)
        except:
            dir = path.dirname(output_file_path)
            if not path.exists(dir):
                makedirs(dir)
                output_image.save(output_file_path)


    # Input and output paths must be directories
    # Assumes that the top level directory of the input contains a patient name that must be renamed and that all sub directory names and filenames do not contain patient names
    def anonymize_patient(self, input_path, output_path):
        debug('Anonymizing patient directory path:  {} ==> {}'.format(input_path, output_path))
        path_list = os.listdir(input_path)

        for dirname, dirnames, filenames in os.walk(input_path):
            # follow path to all subdirectories first.
            for subdirname in dirnames:
                print(os.path.join(dirname, subdirname))

            # then follow path to all filenames.
            for filename in filenames:
                self.anonymize_file(os.path.join(dirname, filename), os.path.join(output_path, filename))
                # print(os.path.join(dirname, filename))

# Input and output paths must be directories
def anonymize_path(input_path, output_path):
    debug('Anonymizing path:  {} ==> {}'.format(input_path, output_path))
    path_list = os.listdir(input_path)

    for dirname, dirnames, filenames in os.walk(input_path):
        # follow path to all subdirectories first.
        for subdirname in dirnames:
            print(os.path.join(dirname, subdirname))

        # then follow path to all filenames.
        for filename in filenames:
            anonymize_file(os.path.join(dirname, filename), os.path.join(output_path, filename))
            # print(os.path.join(dirname, filename))


    # input_image = Image.open(input_file_path)
    # a = numpy.array(input_image)
    # a = numpy.delete(a, slice(20), axis=0)
    # output_image = Image.fromarray(a)
    # output_image.save(output_file_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Vasolabs Controller.",argument_default='anonymize')
    # parser.add_argument('-cfgfile', default='controller.ini', help='Use specified file for configuration.')
    # parser.add_argument('-imagefile', default='image.bmp', help='Use specified image file.')
    # parser.add_argument('-inpath', default='c:\\Users\\jmurray\\imt_studies\\CUPRAK\\Left IMT\\09.39.16 hrs __[0342277].bmp', help='Use specified image file.')
    parser.add_argument('-inpath', default='c:\\Users\\jmurray\\imt_studies\\CUPRAK', help='Use specified image file.')
    # parser.add_argument('-outpath', default='c:\\Users\\jmurray\\anon_imt_studies\\anon1.bmp', help='Use specified image file.')
    parser.add_argument('-outpath', default='c:\\Users\\jmurray\\anon_imt_studies', help='Use specified image file.')
    # parser.add_argument('-path', default='image.bmp', help='Use specified image file.')
    parser.add_argument('action', nargs="?", choices=['anonymize', 'anon'], help='Perform the specified action.')
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
                'backupCount': 5,
                'maxBytes': 100000000,
                'filename': '0.anoymize.log',
                'mode': 'w',
            },
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['file']
        }
    })

    anon = Anon()
    # pseudonym = anon.pseudonym("foozeball")
    # debug("pseudonym: {}".format(pseudonym))

    # daemon = ControllerDaemon(args)
    if 'anonymize' == args.action or 'anon' == args.action:
        if not path.exists(args.inpath):
            raise ValueError('Path does not exist: {}'.format(args.inpath))
        elif not path.exists(path.dirname(args.outpath)):
            raise ValueError('Path does not exist: {}'.format(args.inpath))
        elif path.isfile(args.inpath):
            outpath = args.outpath
            if path.isdir(outpath):
                outpath = path.join(outpath, "newfile.bmp")
            anonymize_file(args.inpath, outpath)
        
        ### Process an input directory to an output directory only
        elif path.isdir(args.inpath) and path.isdir(args.outpath):
            anon.anonymize_patient(args.inpath, path.join(args.outpath, "patient1"))

        else:
            raise ValueError('unsupported path arguments: inpath: {}, outpath: {}'.format(args.inpath, args.outpath))
        
    else:
        raise ValueError('unsupported action: {}'.format(args.action))

#!/usr/bin/env python3

import argparse
import binascii
import hashlib
import os
import re
import struct
import uuid
from logging import debug
from logging.config import dictConfig
from os import makedirs, path, listdir

import numpy
from PIL import Image

default_input_path = r'C:\Users\jmurray\vaso\imt_studies\02-11-20 Wright\CUPRAK, THERESA, 06 08 63F__WRIGHT__[0000082510172102370006842]'
default_input_path = r'C:\Users\jmurray\vaso\imt_studies'
default_output_path = r'C:\Users\jmurray\vaso\anon_studies'

class Anon:
    def __init__(self):
        self.salt = uuid.uuid4().hex.encode('utf-8')
        self.patient_id = 0
        debug("salt: {}".format(self.salt))

    # Create an anonymous
    def pseudonym(self, name):
        hashed_name = hashlib.pbkdf2_hmac('sha256', name.encode(), self.salt, 100000)
        # return hashlib.sha512(name.encode('utf-8') + self.salt.encode('utf-8')).hexdigest()
        # hashed_name = binascii.b2a_base64(struct.pack('i', hash(name)))
        return hashed_name

    def get_new_patient_id(self):
        self.patient_id += 1
        return self.patient_id

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
            # for subdirname in dirnames:
            #     print(os.path.join(dirname, subdirname))

            # then follow path to all filenames.
            for index, filename in enumerate([f for f in filenames if (not ".DS_Store" in f) and (not ".db" in f) and (not "sonologo.gif" in f)]):
                # print(filename)
                subpath = get_subpath(input_path, dirname)
                # print(f"subpath: {subpath}")
                subpath = path.join(output_path, subpath )
                m = re.search(r'(20[0-2]{2})[a-zA-Z]{3}\d{2}\sStudy__\[.*\]', dirname)
                if m:
                    study_year = m.group(1)
                else:
                    study_year = ''
                subpath = re.sub('20[1-2]\d[a-zA-Z]{3}\d+\s*Study__\[\d+\]', repl='mixed', string=subpath)
                updated_filename = re.sub(pattern = '^.*.bmp', repl= str(study_year) + 'image.' + str(index) + ".bmp", string=filename)
                full_filename = path.join(os.path.join(output_path, subpath), updated_filename)
                # print(full_filename)
                self.anonymize_file(os.path.join(dirname, filename), full_filename)
                # print(os.path.join(dirname, filename))

    # Input and output paths must be directories
    def anonymize_path(self, input_path, output_path):
        debug('Anonymizing path:  {} ==> {}'.format(input_path, output_path))
        path_list = os.listdir(input_path)

        for clinic in [f for f in listdir(input_path) if (not ".DS_Store" in f) and (not ".db" in f) and (not "sonologo.gif" in f)]:
            print(f'clinic: {clinic}')
            clinic_path = path.join(input_path, clinic)
            patient_list = os.listdir(clinic_path)
            for patient in [p for p in patient_list if (not ".DS_Store" in p) and (not ".db" in p) and (not "sonologo.gif" in p)]:
                anon.anonymize_patient(path.join(clinic_path, patient), path.join(args.outpath,  "patient-" + str(anon.get_new_patient_id())))

            # # then follow path to all filenames.
            # for filename in filenames:
            #     anonymize_file(os.path.join(dirname, filename), os.path.join(output_path, filename))
            #     # print(os.path.join(dirname, filename))

def get_subpath(base_path, current_path):
    index = current_path.find(base_path)
    subpath = ""
    if index == 0:
        index = len(base_path)
        subpath = current_path[index+1:]
    
    return subpath




    # input_image = Image.open(input_file_path)
    # a = numpy.array(input_image)
    # a = numpy.delete(a, slice(20), axis=0)
    # output_image = Image.fromarray(a)
    # output_image.save(output_file_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Vasolabs Controller.",argument_default='anonymize')
    parser.add_argument('-cfgfile', default='anonymize.ini', help='Use specified file for configuration.')
    # parser.add_argument('-imagefile', default='image.bmp', help='Use specified image file.')
    parser.add_argument('-clinics', default='1', help='Specify number of clinics or the name of a clinic to process or "all"')
    # parser.add_argument('-inpath', default='c:\\Users\\jmurray\\imt_studies\\CUPRAK', help='Use specified image file.')
    # parser.add_argument('-inpath', default=r'V:\jmurray\imt_studies\02-11-20 Wright\CUPRAK, THERESA, 06 08 63F__WRIGHT__[0000082510172102370006842]', help='Use specified image file.')
    parser.add_argument('-inpath', default=default_input_path, help='Use specified image file.')
    # parser.add_argument('-outpath', default='c:\\Users\\jmurray\\anon_imt_studies\\anon1.bmp', help='Use specified image file.')
    # parser.add_argument('-outpath', default=r'V:\jmurray\anon_studies', help='Use specified image file.')
    parser.add_argument('-outpath', default=default_output_path, help='Use specified image file.')
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
            anon.anonymize_path(args.inpath, path.join(args.outpath, "patient" + str(anon.get_new_patient_id())))

        else:
            raise ValueError('unsupported path arguments: inpath: {}, outpath: {}'.format(args.inpath, args.outpath))
        
    else:
        raise ValueError('unsupported action: {}'.format(args.action))

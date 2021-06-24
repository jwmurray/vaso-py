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
from utils import get_config
import pathlib
from datetime import date

import numpy
from PIL import Image

default_input_path = r'C:\Users\jmurray\vaso\imt_studies\02-11-20 Wright\CUPRAK, THERESA, 06 08 63F__WRIGHT__[0000082510172102370006842]'
default_input_path = r'C:\Users\jmurray\vaso\imt_studies'
default_input_path = r'/mnt/dataset/Jolene/Captured Sweeps/MULTI SWEEP 3-18-21'
default_output_path = r'/mnt/dataset/Jolene/Captured Sweeps/MULTI SWEEP 3-18-21'

def convert_func(matchobj):
    this_year = date.today().year
    m =  matchobj.group(1)
    try:
        year = int(m)
    except:
        year = this_year
    
    diff =  this_year - year
    if diff > 89:
        return 90
    else:
        return year

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

    def incr_new_patient_id(self):
        self.patient_id += 1

    def get_new_patient_id(self):
        return self.patient_id

    def get_new_patient_name(self):
        return "patient-" + str(self.patient_id)

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
            dir = os.path.dirname(output_file_path)
            if not os.path.exists(dir):
                makedirs(dir)
                output_image.save(output_file_path)
    



    def anonymize_text_file(self, input_file_path, output_file_path, 
            orig_patient_name, anon_patient_name):
        
        print(f"anonymize txt file: {input_file_path}, output_file_path: {output_file_path}, orig_patient_name: {orig_patient_name}, anon_patient_name: {anon_patient_name}")


        input_files = [f for f in os.listdir(input_file_path) if f[-4:] == ".txt"]
        for file in input_files:
            path = pathlib.Path(output_file_path)
            path.mkdir(parents = True, exist_ok=True)
            out_file = re.sub(f'{orig_patient_name}', anon_patient_name, file, flags=re.IGNORECASE)
            output_file_fullpath = os.path.join(output_file_path, out_file)
            output = open(output_file_fullpath, "w")
            input = open(os.path.join(input_file_path, file))

            for line in input:
                lineout = re.sub(f'^Name: ' + orig_patient_name + r'$', f'Name: {anon_patient_name}', line, flags=re.IGNORECASE)
                ## change dates to years
                lineout = re.sub(r'\d{2}\-\d{2}\-(\d{4})$', r'\1', lineout, count=100)
                line = "7 ate 9"
                new_line =  re.sub(r'\d{2}\-\d{2}\-(\d{4})$', convert_func, line)

                lineout = re.sub(r'^(Patient ID:\s)([a-z]+).*$', r'\1 ' + str(anon.get_new_patient_id()), lineout, flags=re.IGNORECASE,  )
                output.write(lineout)
                # r'$'(.{4})-(.{3})-(.{3})-(.{2})$', r'\1-\4-\2-\3', line))

            input.close()
            output.close()


    # Input and output paths must be directories
    # Assumes that the top level directory of the input contains a patient name that must be renamed and that all sub directory names and filenames do not contain patient names
    def anonymize_patient(self, input_path, output_path):
        debug('Anonymizing patient directory path:  {} ==> {}'.format(input_path, output_path))
        path_list = os.listdir(input_path)

        for dirname, dirnames, filenames in os.walk(input_path):
            for index, filename in enumerate([f for f in filenames if (not ".DS_Store" in f) and (not ".db" in f) and (not "sonologo.gif" in f)]):
                # print(filename)
                subpath = get_subpath(input_path, dirname)
                # print(f"subpath: {subpath}")
                subpath = os.path.join(output_path, subpath )
                m = re.search(r'(20[0-2]{2})[a-zA-Z]{3}\d{2}\sStudy__\[.*\]', dirname)
                if m:
                    study_year = m.group(1)
                else:
                    study_year = ''
                subpath = re.sub('20[1-2]\d[a-zA-Z]{3}\d+\s*Study__\[\d+\]', repl='mixed', string=subpath)
                updated_filename = re.sub(pattern = '^.*.bmp', repl= str(study_year) + 'image.' + str(index) + ".bmp", string=filename)
                full_filename = os.path.join(os.path.join(output_path, subpath), updated_filename)
                self.anonymize_file(os.path.join(dirname, filename), full_filename)

    # Input and output paths must be directories
    def anonymize_path(self, input_path, output_path):
        debug('Anonymizing path:  {} ==> {}'.format(input_path, output_path))
        path_list = os.listdir(input_path)

        for clinic in [f for f in listdir(input_path) if (not ".DS_Store" in f) and (not ".db" in f) and (not "sonologo.gif" in f)]:
            print(f'clinic: {clinic}')
            clinic_path = os.path.join(input_path, clinic)
            patient_list = os.listdir(clinic_path)
            for patient in [p for p in patient_list if (not ".DS_Store" in p) and (not ".db" in p) and (not "sonologo.gif" in p) and (not "zz" in p)]:
                patient_match = re.search(r'(.*?), \d', patient)
                if(patient_match):
                    patient_name = patient_match.group(1)
                else:
                    raise Exception("Could not find patient in path.")
                self.incr_new_patient_id()
                anon_patient_name = "patient-" + str(self.get_new_patient_id())
                self.anonymize_patient(os.path.join(clinic_path, patient), 
                    os.path.join(output_path,  anon_patient_name))
                self.anonymize_text_file(input_file_path = os.path.join(clinic_path, patient), 
                    output_file_path= os.path.join(output_path, anon_patient_name),
                    anon_patient_name= anon_patient_name, orig_patient_name=patient_name)
                
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

    foo = get_config("anonymize.ini")

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
                outpath = os.path.join(outpath, "newfile.bmp")
            anonymize_file(args.inpath, outpath)
        
        ### Process an input directory to an output directory only
        elif path.isdir(args.inpath) :
            path = pathlib.Path(args.outpath)
            path.mkdir(parents = True, exist_ok=True)
            anon.anonymize_path(args.inpath, args.outpath)

        else:
            raise ValueError('unsupported path arguments: inpath: {}, outpath: {}'.format(args.inpath, args.outpath))
        
    else:
        raise ValueError('unsupported action: {}'.format(args.action))

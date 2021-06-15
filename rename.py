#!/usr/bin/env python3

from glob import glob
import shutil
import os
from posixpath import basename
import re

files = glob("c:\\Users\\jmurray\\vaso\\imt_studies\\**\*.txt", recursive=True)
for name in files:
    lowername = name.lower()
    dirpath = os.path.dirname(name)
    basename = os.path.basename(name)
    clinicpath = os.path.dirname(dirpath)
    print(f"clinicpath: {clinicpath}")
    old_name = os.path.join("{}".format(name))
    print(f"old name: {old_name}")
    name_lower = name.lower()

    analyst_match = re.search(" (kalli|lindy|janice|kristin)", name_lower)
    if analyst_match:
        analyst = analyst_match.group(1)
    else:
        raise Exception("Analyst unknown")

    patient_match = re.search(r'^.*[\/|\\](.*)\-(l|r)\.txt', name_lower)
    if patient_match:
        patient = patient_match.group(1)
        print(f'Patient: {patient}')
    else:
        patient = "unknown_patient"
        if patient == "unkown_patient":
            raise(f"unknown_patient: {patient_match}")    

    patientdirs = os.listdir(clinicpath)
    for dir in patientdirs:
        if patient.lower() in dir.lower():
            patient_dir = dir
            break
    
    
    patient_path = os.path.join(clinicpath, patient_dir)
    if not os.path.exists(patient_path) or not os.path.exists(old_name):
        raise Exception("path does not exist")
    
    new_name =  os.path.join(patient_path, "{}".format("{}-{}".format(analyst, basename)))
    print("new name: ", new_name)
    shutil.copy(old_name, new_name)
    
    
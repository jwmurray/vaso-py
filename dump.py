#!/usr/bin/python

import argparse
import RestToolbox
import json
import pprint
import pandas as pd

default_url = "http://172.16.2.8:8043"
defautl_target = "/tmp/Archive.zip"


parser = argparse.ArgumentParser(description="Dump Orthanc server.")
parser.add_argument('--url"', default="http://172.16.2.8:8043", help='Use specified file for configuration')
parser.add_argument('--patients', default=False, action="store_true", help='dump patients')
parser.add_argument('--studies', default=False, action="store_true", help='dump studies')
parser.add_argument('--clinics', default=False, action="store_true", help='dump clinics')
parser.add_argument('--doctors', default=False, action="store_true", help='dump doctors')

# args = parser.parse_args()
args = parser.parse_args(['--patients'])

print(args)

URL = default_url
TARGET = defautl_target

username='jmurray'
password='beaver89'
RestToolbox.SetCredentials(username, password)
patients = RestToolbox.DoGet('{}/patients'.format(URL))

patient_dict = {}

if args.patients:
    print('Dumping patients...')
    for count,patient in enumerate(patients):
        patient = RestToolbox.DoGet('{}/patients/{}'.format(URL, patient))

        patient_name = patient["MainDicomTags"]["PatientName"]
        patient_dob = patient["MainDicomTags"]["PatientBirthDate"]
        patient_id = patient["MainDicomTags"]["PatientID"]
        key = patient_id

        if 'OtherPatientIDs' in patient["MainDicomTags"]:
            clinic_name = patient["MainDicomTags"]['OtherPatientIDs']
        else:
            clinic_name = "not available"

        if key in patient_dict:
            print("Duplicate key in dictionary {}".format(key))
        

        patient_dict[key] = patient
        print(f"{count}. {patient_name} - {patient_dob} - {patient_id}")
        

        for study_id in patient["Studies"]:
            study = RestToolbox.DoGet('{}/studies/{}'.format(URL, study_id))
            if 'ReferringPhysicianName' in study['MainDicomTags']:
                referringPhysician = study['MainDicomTags']['ReferringPhysicianName']
            else:
                referringPhysician = "Not Available"
            print(f"\tStudy: {study_id} - Clinic: {clinic_name}, Doc: {referringPhysician}, StudyDate: {study['MainDicomTags']['StudyDate']}")

            for series_id in study["Series"]:
                series = RestToolbox.DoGet('{}/series/{}'.format(URL, series_id))
                instance_count = len(series['Instances'])
                print(f"\t\tSeries: {series_id} - {series['MainDicomTags']['Manufacturer']}, Modality: {series['MainDicomTags']['Modality']} - {series['MainDicomTags']['OperatorsName']} - ({instance_count})")

                # Print all instances
                # for instance_id in series["Instances"]:
                #     instance = RestToolbox.DoGet('{}/instances/{}'.format(URL, instance_id))
                #     print(f"\t\t\t{instance_id} - {instance['MainDicomTags']['InstanceCreationDate']}, {instance['MainDicomTags']['InstanceNumber']}")



print("Count of parent_dict is {}".format(len(patient_dict)))


mylist = [ f"{v['MainDicomTags']['PatientName']:30}DOB-{v['MainDicomTags']['PatientBirthDate']:10}PID-{v['MainDicomTags']['PatientID']}" for k,v in patient_dict.items()]
print('\n'.join(map(str, sorted(mylist))))

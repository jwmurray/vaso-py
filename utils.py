#!/usr/bin/env python3
import platform
from configparser import ConfigParser

def get_config(cfgfile):
    config = ConfigParser()
    config.read(cfgfile)
    clinics = default.clinics()
    
    if hostname not in config: raise KeyError('no host configuration for "{}"'.format(hostname))
    conf = { **config.defaults(),
             **dict([(key, config.get(hostname, key)) for key in config.options(hostname)]) }
    conf['orthanc-auth-required'] = config.getboolean('DEFAULT', 'orthanc-auth-required')
    if conf['orthanc-auth-required']:
        conf['orthanc-username'] = config.get('DEFAULT', 'orthanc-username')
        conf['orthanc-password'] = config.get('DEFAULT', 'orthanc-password')
    conf['dicom-file-base'] = config.get('DEFAULT', 'dicom-file-base')
    conf['image-file-base'] = config.get('DEFAULT', 'image-file-base')
    conf['sleep-interval-secs'] = config.getint('DEFAULT', 'sleep-interval-secs')
    conf['gmail-username'] = config.get('DEFAULT', 'gmail-username')
    conf['gmail-password'] = config.get('DEFAULT', 'gmail-password')
    conf['orthanc-base-url'] = config.get(hostname, 'orthanc-base-url')
    conf['dicom-dir-format'] = config.get(hostname, 'dicom-dir-format')
    conf['zip-output-file'] = config.get(hostname, 'zip-output-file')
    conf['worker-output-dir'] = config.get(hostname, 'worker-output-dir')
    conf['db-name'] = config.get(hostname, 'db-name')
    conf['db-user'] = config.get(hostname, 'db-user')
    conf['db-pass'] = config.get(hostname, 'db-pass')
    conf['pg-remote'] = config.getboolean(hostname, 'pg-remote')
    if conf['pg-remote']: conf['pg-port'] = config.getint(hostname, 'pg-port')
    conf['need-extraction-email'] = config.getboolean(hostname, 'need-extraction-email')
    return conf

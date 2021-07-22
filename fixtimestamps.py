import os
import glob
import shutil
import time
import re


def replfunc(matchobj):
    # return matchobj.group(1) + "." + matchobj.group(0)
    count = 0
    for count in range(matchobj.lastindex + 1):
        print(f"group{count}: {matchobj.group(count)}")
        count += 1
    returnstr = ""
    if matchobj.lastindex > 3 and matchobj.group(4) != None:
        returnstr += matchobj.group(4)  
    if matchobj.group(2) != None:
        returnstr +=  r"." + matchobj.group(2) 
    # if matchobj.group(1) != None:
    #     returnstr +=  r"." + matchobj.group(1) 
    if matchobj.lastindex > 3 and  matchobj.group(4) != None:
        returnstr += r"." + matchobj.group(4)
    
    print(f"returnstr: {returnstr}")
    return  returnstr

basedir = r's:/jmurray/DicomFiles-vmserver/2021-06'
outputdir = r's:/jmurray/DicomFiles-vmserver/2021-06'

basedir = r'/mnt/dataset/jmurray/DicomFiles-vmserver/2021-06'
basedir = r'/mnt/dataset/jmurray/vaso/test'
basedir = r'/mnt/dataset/jmurray/DicomFiles-vmserver/2021-06'
outputdir = r'/mnt/dataset/jmurray/DicomFiles-vmserver/2021-06'

search_for_trailing_indcies = r'(^\d{2}\.\d{3}\-\d{3}\.bmp)(?:\.)+?(.*?)(\.*?)(\d{2}\.\d{3}\-\d{3}\.bmp)'

print(f"Directory: {dir}")
# listing = os.listdir(dir)
searchpath = basedir + r'/**/*.dicom'

for root, dirs, files in os.walk(basedir):
    level = root.replace(basedir, '').count(os.sep)
    indent = ' ' * 4 * (level)
    print('{}{}/'.format(indent, os.path.basename(root)))
    subindent = ' ' * 4 * (level + 1)
    for file in sorted(files):
        old_filename = file
        # matchobj = re.search(pattern = r'^(\d{2}\.\d{3}\-\d{3}\.bmp\.)(\.*?)(.*)(\d{2}\.\d{3}\-\d{3}\.bmp)', string=old_filename)
        matchobj = re.search(pattern = search_for_trailing_indcies, string=old_filename)
        if not matchobj:
            continue

        print(f"old: {old_filename}")
        new_filename = re.sub(search_for_trailing_indcies, replfunc, old_filename)
        # new_filename = re.sub(r'(\d{2}\.\d{3}\-\d{3}\.bmp\.)(.*)(\d{2}\.\d{3}\-\d{3}\.bmp)', replfunc, old_filename)
        old_filepath = os.path.join(root,old_filename)
        new_filepath = os.path.join(root,new_filename)
        if old_filename != new_filename:
            if True:
                os.rename(old_filepath, new_filepath)
                mod_time = os.path.getmtime(new_filepath)
                mod_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mod_time))
                print('{}:  {}{}'.format(mod_time_str, subindent, new_filename))

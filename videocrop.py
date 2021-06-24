import os
import glob


basedir = r'/mnt/dataset/Jolene/Captured Sweeps'
outputdir = r'/mnt/dataset/jmurray/Anon_Captured_Sweeps'

print(f"Directory: {dir}")
# listing = os.listdir(dir)
glo = glob.glob(basedir + r'/**/*.mp4', recursive=True)
# glo = glob.glob(basedir + r'\*.zip', recursive=True)
# print(listing)
ending = "mp4"
outfile_count = 1
for file in glo:
    print(file)
    basename = os.path.basename(file)
    outfile = os.path.join(outputdir, f"video-{outfile_count}.{ending}")
    outfile_count += 1
    cmd = f'ffmpeg -y -i "{file}" -filter:v "crop=640:460:0:20" {outfile}'
    print(f"cmd: {cmd}")
    os.system(cmd)    

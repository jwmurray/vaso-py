import os
import binaryfile
import re
import glob


def bmp(b):
    b.byteorder = 'little'
    b.uint('ID', 2)    # 0x00
    b.uint('size', 4)  # 0x02
    b.uint('unused1', 2 ) # 0x06
    b.uint('unused2', 2 ) # 0x08
    b.uint('pixel_array_offset', 4 ) #0x0a
    b.uint('dib_header_size', 4 ) #0x0e
    b.uint('width', 4 ) #0x12
    b.uint('height', 4 ) #0x16
    b.uint('color_plane_count', 2) # 0x1A
    b.uint('bits_per_pixel', 2)  # 0x1C
    b.uint('BI_BITFIELDS', 4)  # 0x1E
    b.uint('bitmap_size', 4) # 0x22
    b.uint('print_res_horiz', 4) # 0x26
    b.uint('print_res_vert', 4) # 0x2A

def get_26(filename):
    match = re.search(pattern=r'^.*\.bmp$', string = filename)
    if not match:
        return 0,"bmp not found"
    else:
        with open(filename, 'rb') as fh:
	        data = binaryfile.read(fh, bmp)
        if data.print_res_horiz != data.print_res_vert:
            print("0x26 and 0x2a do not match for file {}",format(filename))
            print("horiz: " + str(data.print_res_horiz))
            print("vert: " + str(data.print_res_vert))
            return 0, 0, 0, None
        match = re.search(r'.*?\[(\d{7})\]\.bmp', os.path.basename(filename))
        if match:
            clip_index = int(match.group(1))
            # clip_string = f"{clip_index:02x}"
        else:
            clip_index = 0
            # clip_string = f"No Clip_index provided"
        return clip_index, data.print_res_horiz, data.print_res_vert, data




def main():
    search_path = r'S:/jmurray/vaso/imt_studies'
    # files = glob.glob(pathname=search_path, recursive=True)
    lowv = 0
    lowh = 0
    highv = 0
    highh=0

    for root, dirs, files in os.walk(search_path):
        filtered_files = [f for f in files if r'bmp' in f]
        for file in filtered_files:
            
            full_file = os.path.join(root, file)
            

            clip_index, horiz, vert, data = get_26(full_file)
            if lowv == 0:
                lowv = vert
                lowh = horiz
                highv = vert
                highh=horiz

            if horiz > highh:
                highh = horiz
            if vert > highv:
                highv = vert
            if horiz < lowh and horiz != 0:
                lowh = horiz
            if vert < lowv and vert != 0:
                lowv = vert


            if horiz is not None:
                print(f"horiz: 0x{horiz:08x}, vert:{vert:02x}, highv:{highh:02x}, highv:{highv:02x}, lowh:{lowh:02x}, lowv:{lowv:02x}"
                    f" - 0x{clip_index:08x} - {clip_index} ")





if __name__ == "__main__":
    main()
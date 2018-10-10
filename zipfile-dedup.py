#!python3

import argparse
import os
import subprocess
import sys
import zipfile

del_pref = "del_"
save_file_pref = "/temp/"
z7z_name = 'c:/program files/7-zip/7z'

def get_files():
    parser = argparse.ArgumentParser(description="Program to deduplicate redundant files using a pair of zip files. "+
                                     "Identical files found in both zip files will be de-duped from the 'old' file.")
    parser.add_argument('--old',    '-o', dest='file_1', required=True, type=str, nargs=1,
                        help="Old file to be 'de-duped'.")
    parser.add_argument('--recent', '-r', dest='file_2', required=True, type=str, nargs=1,
                        help="Recent file used as the most recent master, and will remain untouched.")
    args = parser.parse_args()
#   print(args.file_1, args.file_2)
    return args.file_1[0], args.file_2[0]

def verify_zipfile(filename):
    if zipfile.is_zipfile(filename):
#       print(filename, "is a valid zipfile.")
        return True
    else:
        print(filename, "is not present or is not a valid zipfile.")
    return False

def print_summary(f_count, dir_count, nf_count, update_count, del_count):
    print("\nRecent file summary")
    print(  "===================")
    print(f_count, "files reviewed.")
    print(dir_count, "directories.")
    print(nf_count, "new files.")
    print(update_count, "files with updated timestamps.")
    print(del_count, "files to be deleted.")
   
def zip_open(filename):
    return zipfile.ZipFile(filename, mode='r')

def format_date(dt):   # dt = date tuple
    date = ""
    date = str(dt[0]) + "/" + str(dt[1]) + "/" + str(dt[2]) + " " + str(dt[3]) + ":" + str(dt[4])+ ":"  + str(dt[5]) 
    return date   

def is_directory(item):
    try:
        is_directory = item.is_dir()
    except AttributeError:
        is_directory = item.filename[-1] == "/"

    return is_directory

def delete_this_file(item):
    return ".DS_Store" in item.filename or \
           "/@"        in item.filename or \
           f_file_old.getinfo(item.filename).date_time == f_file_recent.getinfo(item.filename).date_time

#------------------------------------------------------

print()  # blank line

file_old, file_recent = get_files()  # The get_files procedure will abort in argparse if parameters are wrong.
                                     # Hence no error checking needed.

#print("old="+file_old, "recent="+file_recent)
 
if verify_zipfile(file_old) & verify_zipfile(file_recent):
#   print("Files validated")
    pass
else:
    sys.exit()

save_file = save_file_pref + os.path.basename(file_old)

#    Open delete list file
del_listfile = del_pref + os.path.basename(file_old) + ".txt"
del_file = open(del_listfile, "w", encoding="UTF-8")   # write utf-8 mode since 7-zip can read that form


f_file_old    = zip_open(file_old)
f_file_recent = zip_open(file_recent)
  
#    Init/Reset counters
f_count, dir_count, nf_count, update_count, del_count = 0, 0, 0, 0, 0

# Loop through files in "recent" and lookup in "old"
for item in f_file_recent.infolist():
    if is_directory(item):
        dir_count += 1
#       print("\n" + item.filename, "is a directory")
        continue # ignore, it's a directory
    
    f_count += 1
    print(" ", f_count, end='\r')

#   Is the current file in the old zip file?
    try:
        f_file_old.getinfo(item.filename)
#       print("File present in", file_old)
    except KeyError:
        nf_count += 1
#       print("File not in 'recent':", item.filename)
        continue

    if delete_this_file(item):
    # We want to delete this file in the update
        del_count += 1
        print(item.filename, file=del_file)
    else:  # print out differing dates for the file.
        update_count += 1
#       f_old_date = format_date(f_file_old.getinfo(item.filename).date_time)
#       f_rec_date = format_date(f_file_recent.getinfo(item.filename).date_time)
#       print(f_old_date, ";", f_rec_date, item.filename)

#Clear line
print("              ", end='\r')

del_file.close()
f_file_old.close()    # must close, or else 7-zip update fails with file open.
f_file_recent.close()

print_summary(f_count, dir_count, nf_count, update_count, del_count)

if del_count > 0:
    print("---------------------------------------")
    # Start 7-zip, in a synchronous co-routine (that is:, wait for it to finish before completing the dedupe progam)
    subprocess.call([z7z_name, "d", file_old, "-u-", "-u!" + save_file, "@" + del_listfile])

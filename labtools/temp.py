from pathlib import Path
import glob
import shutil

basedir = '/Volumes/Data/pdssp/psup/source/mars/mex_omega_cubes_rdr'
backupdir = '/Volumes/Data/pdssp/psup/backup/source/mars/mex_omega_cubes_rdr/data'
list_file = Path(basedir) / 'list.txt'
products_list = []
if list_file.exists():
    with open(list_file) as f:
        products_list = [line.rstrip() for line in f]

datadir = Path(basedir) / 'data/*.nc'
nc_files = glob.glob(str(datadir))

n = 0
m = 0
for nc_file in nc_files:
    if Path(nc_file).name in products_list:
        n += 1
    else:
        dstfile = str(Path(backupdir) / Path(nc_file).name)
        print(f'File moved')
        print(f'from : {nc_file}')
        print(f'to   : {dstfile}')
        print()
        shutil.move(nc_file, dstfile)
        m += 1
print()
print(n)
print(m)
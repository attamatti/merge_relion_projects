#!/usr/bin/env python

import sys
import subprocess
import os
import glob

###---------function: read the star file get the header, labels, and data -------------#######
def read_starfile_new(f):
    inhead = True
    alldata = open(f,'r').readlines()
    labelsdic = {}
    data = []
    header = []
    count = 0
    labcount = 0
    for i in alldata:
        if '_rln' in i:
            labelsdic[i.split()[0]] = labcount
            labcount +=1
        if inhead == True:
            header.append(i.strip("\n"))
            if '_rln' in i and '#' in i and  '_rln' not in alldata[count+1] and '#' not in alldata[count+1]:
                inhead = False
        elif len(i.split())>=1:
            data.append(i.split())
        count +=1
    
    return(labelsdic,header,data)
#---------------------------------------------------------------------------------------------#

errmsg = '''
USAGE: rln-clone-dir <joined particles starfile> <project dir 1> <project dir 2> ... <project dir n>

the project dirs where all of the paticles originally came from need to be included
'''

## check the starfile
try:
	labels,header,stardata= read_starfile_new(sys.argv[1])	
except:
	sys.exit("\nERROR reading starfile {0}".format(errmsg))

## check that the original project dir data paths exists
datapaths = sys.argv[2:]
errors = []
for i in datapaths:
		if os.path.isdir(i) == False:
			errors.append('\nERROR: {0} is not a valid directory')
if len(errors) > 0:
	sys.exit('{0}{1}'.format('\n'.join(errors),errmsg))
else:
	datapaths = [os.path.abspath(x) for x in datapaths]
	print('\n{0} project dirs found'.format(len(datapaths)))	
	for i in datapaths:
		print(':: {0}'.format(i))
if len(datapaths) == 0:
	sys.exit('\nERROR: No project dir data paths found {0}'.format(errmsg))

## get the list of all the files that need to be linked 
particle_files = []
rawdata_files = []
mocorr_files = []

for i in stardata:
	particle_files.append(i[labels['_rlnImageName']].split('@')[-1])
	mocorr_files.append(i[labels['_rlnMicrographName']])
	rawdata_files.append('/'.join(i[labels['_rlnMicrographName']].split('/')[-2:]))


## check that linked files exist
sys.stdout.write('\nFinding linked files')
sys.stdout.flush()
n=0
missed = []
sys.stdout.write('...particle files')
sys.stdout.flush()
for i in particle_files:
	found = False
	for j in datapaths:
		if os.path.isfile('{0}/{1}'.format(j,i)) == True:
			particle_files[n] = '{0}/{1}'.format(j,i)
			found = True
	if found == False:
		missed.append(i)
	n+=1
n=0
missed = []
sys.stdout.write('...mocorr files')
sys.stdout.flush()
for i in mocorr_files:
	found = False
	for j in datapaths:
		if os.path.isfile('{0}/{1}'.format(j,i)) == True:
			mocorr_files[n] = '{0}/{1}'.format(j,i)
			found = True
	if found == False:
		missed.append(i)
	n+=1
n=0
missed = []
sys.stdout.write('...raw data files')
sys.stdout.flush()
for i in rawdata_files:
	found = False
	for j in datapaths:
		if os.path.isfile('{0}/{1}'.format(j,i)) == True:
			rawdata_files[n] = '{0}/{1}'.format(j,i)
			found = True
	if found == False:
		missed.append(i)
	n+=1
if len(missed) > 0:
	print('\nThe following files were not found in any of the project dirs:')
	for i in missed:
		print(i)
	sys.exit('{0} files were missing'.format(len(missed)))
else:
	print('...All linked files found!\n')

## build the required directory structure
extractdirs,rawdirs,mocorrdirs = [],[],[]
for i in particle_files:
	if i.split('/')[-3:-1] not in extractdirs:
		extractdirs.append(i.split('/')[-3:-1])
for i in mocorr_files:
	if i.split('/')[-3:-1] not in mocorrdirs:
		mocorrdirs.append(i.split('/')[-3:-1])
for i in rawdata_files:
	if (i.split('/')[-2]) not in rawdirs:
		rawdirs.append(i.split('/')[-2])
print('Building directory structure')
for i in extractdirs:
	print (':: Extract/{0}'.format('/'.join(i)))
for i in mocorrdirs:
	print (':: MotionCorr/{0}'.format('/'.join(i)))
for i in rawdirs:
	print(':: {0}'.format(i))

if os.path.isdir('Extract') == False:
	subprocess.call(['mkdir','Extract'])
if os.path.isdir('MotionCorr') == False:
	subprocess.call(['mkdir','MotionCorr'])
for i in rawdirs:
	if os.path.isdir(i) == False:
		subprocess.call(['mkdir',i])
for i in extractdirs:
	for j in range(len(i)):
		if os.path.isdir('Extract/{0}'.format('/'.join(i[0:j]))) == False:
			subprocess.call(['mkdir','Extract/{0}'.format('/'.join(i[0:j]))])		
	if 	os.path.isdir('Extract/{0}'.format('/'.join(i[0:]))) == False:
		subprocess.call(['mkdir','Extract/{0}'.format('/'.join(i[0:]))])
for i in mocorrdirs:
	for j in range(len(i)):
		if os.path.isdir('MotionCorr/{0}'.format('/'.join(i[0:j]))) == False:
			subprocess.call(['mkdir','MotionCorr/{0}'.format('/'.join(i[0:j]))])	
	if 	os.path.isdir('MotionCorr/{0}'.format('/'.join(i[0:]))) == False:
		subprocess.call(['mkdir','MotionCorr/{0}'.format('/'.join(i[0:]))])
## symbolic link all the files
print('\nLinking files')
sys.stdout.write(':: Particle files')
sys.stdout.flush()
for i in particle_files:
	targetdir = '/'.join(i.split('/')[-4:-1])
	if os.path.isfile('/'.join(i.split('/')[-4:])) == False:	
		subprocess.call(['ln','-s',i,targetdir])
sys.stdout.write('...{0} files\n'.format(len(particle_files)))
sys.stdout.flush()

sys.stdout.write(':: MotionCorr files')
sys.stdout.flush()
for i in mocorr_files:
	targetdir = '/'.join(i.split('/')[-4:-1])
	if os.path.isfile('/'.join(i.split('/')[-4:])) == False:	
		subprocess.call(['ln','-s',i,targetdir])
sys.stdout.write('...{0} files\n'.format(len(mocorr_files)))
sys.stdout.flush()

sys.stdout.write(':: Raw data files')
for i in mocorr_files:
	targetdir = i.split('/')[-2]
	if os.path.isfile('/'.join(i.split('/')[-2:])) == False:	
		subprocess.call(['ln','-s',i,targetdir])
sys.stdout.write('...{0} files\n'.format(len(mocorr_files)))
sys.stdout.flush()

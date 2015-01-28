from __future__ import print_function
from StringIO import StringIO
from os.path import exists
from urllib2 import urlopen
from zipfile import ZipFile
from scipy import stats
from json import dumps
from sys import stdout
from csv import reader

# TODO: Handle ICD-9 code changes over time.

# Source: http://quickstats.nass.usda.gov/
glyphosate = {
	1996:  1421, # Data.
	1997:  1500, # Data.
	1998:  2190, # Data.
	1999:  2695, # Interpolated.
	2000:  3200, # Data.
	2001:  2488, # Interpolated.
	2002:  1776, # Data.
	2003:  3730, # Interpolated.
	2004:  5685, # Data.
	2005:  6950, # Interpolated.
	2006:  8215, # Data.
	2007: 11375, # Interpolated.
	2008: 14535, # Interpolated.
	2009: 17695, # Data.
	2010: 16725, # Interpolated.
}

codes = 'https://raw.githubusercontent.com/freemed/freemed/master/data/multum/hcfa_icd_9.csv'

# See: ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/NHDS/
datasets = {
	1996: 'ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHDS/nhds96/nhds96.zip',
	1997: 'ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHDS/nhds97/nhds97.zip',
	1998: 'ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHDS/nhds98/nhds98.zip',
	1999: 'ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHDS/nhds99/nhds99.zip',
	2000: 'ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHDS/nhds00/nhds00.zip',
	2001: 'ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHDS/nhds01/nhds01.zip',
	2002: 'ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHDS/nhds02/NHDS02PU.zip',
	2003: 'ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHDS/nhds03/NHDS03PU.zip',
	2004: 'ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHDS/nhds04/NHDS04PU.zip',
	2005: 'ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHDS/nhds05/NHDS05.PU.TXT',
	2006: 'ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHDS/nhds06/NHDS06.PU.TXT',
	2007: 'ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHDS/nhds07/NHDS07_PUF.txt',
	2008: 'ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHDS/nhds08/NHDS08.PU.txt',
	2009: 'ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHDS/nhds09/NHDS09.PU.TXT',
	2010: 'ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHDS/nhds10/NHDS10.PU.txt',
}

icd9 = {}

name = 'cache/icd9.csv'
if not exists(name):
	print('  Downloading %s' % name)
	response = urlopen(codes)
	with open(name, 'w') as cache:
		cache.write(response.read())
	response.close()
print('  Parsing %s' % name)
with open(name) as file:
	csv = reader(file)
	csv.next() # Skip header row.
	for row in csv:
		icd9[row[0].replace('.', '')] = row[1]

data = {}
totals = {}

for year, url in datasets.iteritems():
	name = 'cache/ndhs-%s.txt' % year
	if not exists(name):
		print('  Downloading %s' % name, end='\r')
		stdout.flush()
		response = urlopen(url)
		if url.endswith('.zip'):
			zip = ZipFile(StringIO(response.read()))
			response = zip.open(zip.namelist()[0])
		with open(name, 'w') as cache:
			count = 0
			for line in response:
				count += 1
				if count % 1000 == 0:
					print('  Downloading %s (%d)' % (name, count), end='\r')
					stdout.flush()
				cache.write(line)
		print('  Downloaded %s            ' % name)
		response.close()
	with open(name) as cache:
		count = 0
		for line in cache:
			count += 1
			if count % 1000 == 0:
				print('  Processing %s (%d)' % (name, count), end='\r')
				stdout.flush()
			for i in range(28, 62, 5):
				code = line[i - 1:i + 4].strip(' -')
				if not code:
					continue # Empty diagnosis slot.
				if not code in data:
					data[code] = {} # Initialize code.
				if not year in data[code]:
					data[code][year] = 0 # Initialize year.
				data[code][year] += 1 # Increment.
		totals[year] = count / 100000.0 # Per one hundred thousand.
		print('  Processed %s          ' % name)

count = 0
num = len(data)
for code, years in data.iteritems():
	name = 'data/%s.json' % code
	count += 1
	if count % 10 == 0:
		print('  Saving (%d of %d) %s     ' % (count, num, name), end='\r')
		stdout.flush()
	graph = []
	glyphosate_d = []
	graph_d = []
	for year, scale in totals.iteritems():
		if year in years:
			graph.append([year, years[year] / scale])
			glyphosate_d.append(glyphosate[year])
			graph_d.append(years[year])
	if len(graph) < 3:
		continue # Not enough data.
	_, _, r_value, p_value, _ = stats.linregress(glyphosate_d, graph_d)
	if r_value < 0.9 and r_value > -0.9:
		continue # Unimpressive R-value.
	if p_value > 0.05:
		continue # Unimpressive P-value.
	label = code
	if code in icd9:
		label = '%s - %s'% (code, icd9[code])
	with open(name, 'wb') as file:
		file.write(dumps({
			'label': label,
			'data': graph,
			'rval': r_value,
			'pval': p_value,
		}))
print('  Saved %d code files                 ' % num)

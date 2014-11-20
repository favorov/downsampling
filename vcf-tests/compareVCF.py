#Created: 7.23.13
#Last Modified: 5.12.14

import sys
import os
from collections import defaultdict
import argparse

def main(args):
  global verbose, path, goldstandard, repos, sizes, boxplot, barchart, varDistance, distanceOut
  verbose = args.argVerbose
  root = args.argRootOutput
  path = args.argPath
  goldstandard = args.argGoldstandard

  boxplot = open(root + '.box.txt', 'w')
  barchart = open(root + '.bar.txt', 'w')
  #posOut = open(root + '.pos.txt', 'w')
  #negOut = open(root + '.neg.txt', 'w')
  distanceOut = open(root + '.distance.txt', 'w')

  repos = defaultdict(int)
  sizes = {}
  varDistance = defaultdict(int)

  for root, dirs, files in os.walk(path):
    for file in files:
      if file[0] != '.':
        if verbose:
          print('Comparing ' + file + ' to ' + goldstandard + '...')
        filesize = int(file.split('_')[-3])
        sizes.setdefault(filesize, 0)
        sizes[filesize] += 1
        falsePos, falseNeg = compare(file, filesize)
        output = str(file) + '\t' + str(filesize) + '\t' + str(falsePos) + '\t' + str(falseNeg) + '\n'
        boxplot.write(output)

  if verbose:
    print('Processing Results...')
  processRepository()
  boxplot.close()
  barchart.close()
  if verbose:
    print('Complete')

def parseArguments():
  parser = argparse.ArgumentParser(description='Analyze a directory of vcf files.', usage='%(prog)s [options] -p <path> -s <standard>')
  required = parser.add_argument_group('required arguments')
  group = parser.add_mutually_exclusive_group()
  group.add_argument('-q', '--quiet', action='store_false', help='current status is not printed to standard output', dest='argVerbose')
  group.add_argument('-v', '--verbose', action='store_true',  help='print current status to standard output [Default]', dest='argVerbose')
  parser.add_argument('-o', '--output', default='compareVCFResults', help='the root name to use for output files', metavar='', dest='argRootOutput') 
  required.add_argument('-p', '--path', required=True, help='path to the directory of vcf files', metavar='', dest='argPath')
  required.add_argument('-s', '--standard', required=True, help='file to which each vcf is compared', metavar='', dest='argGoldstandard')

  return parser.parse_args()

def skipPound(f):
  cur = f.readline()
  while len(cur) > 0 and cur[0] == '#':
    cur = f.readline()
  return cur.split()


"""
Opens a new instance of the standard file and the file to test. Compares the files line by line.
  Determines which file is "ahead" by compareing chromosomes, then positions, then if is an "INDEL".
  If standard is ahead then increment false positives. Add position to repository.
  If test is ahead then increment false negatives. Add position to repository.
Close both files.
Return number of false positives and false negatives.

False positive and negative positions are stored in a dictionary using a tuple of (downsampleSize, chromosome, position, isINDEL)
  as a key. Each time the same tuple occurs the count is updated.
"""
def compare(tf, size):
  testFile = open(path+tf)
  standardFile = open(path+goldstandard)
  test = skipPound(testFile)
  standard = skipPound(standardFile)

  #covReposPos = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  #covReposNeg = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

  fPos = 0
  fNeg = 0

  lastVariant = 0

  while not (len(test) <= 0 and len(standard) <= 0):
    
    #Special Case: One of the files has hit the end.
    if len(test) <= 0:
      fNeg += 1 
      temp = standard[7][standard[7].find('DP='):]
      coverage = int(temp[3: temp.find(';')])
      #if coverage > 0 and coverage <= 400:
        #covReposNeg[int((coverage-1)/20)] += 1
      #else:
        #covReposNeg[20] += 1
      repos[(size, standard[0], standard[1], str(standard[7][0:5]=='INDEL'))] += 1
      if int(standard[1]) >= lastVariant:
        varDistance[(size, int(standard[1])-lastVariant)] += 1
        lastVariant = int(standard[1])
      else:
        lastVariant = 0
      standard = standardFile.readline().split()
    elif len(standard) <= 0:
      fPos += 1
      temp = test[7][test[7].find('DP='):]
      coverage = int(temp[3: temp.find(';')])
      #if coverage > 0 and coverage <= 400:
        #covReposPos[int((coverage-1)/20)] += 1
      #else:
        #covReposPos[20] += 1 
      repos[(size, test[0], test[1], str(test[7][0:5]=='INDEL'))] += 1
      if int(test[1]) >= lastVariant:
        varDistance[(size, int(test[1])-lastVariant)] += 1
        lastVariant = int(test[1])
      else:
        lastVariant = 0
      test = testFile.readline().split()
    else:
      #Allow chromosomes to be compared based on integer value.
      testchrom = test[0][3:]
      try:
        testnum = int(testchrom)
      except ValueError:
        if testchrom == 'X':
          testnum = 24
        elif testchrom == 'Y':
          testnum = 25
        elif testchrom == 'M':
          testnum = 26

      standchrom = standard[0][3:]
      try:
        standnum = int(standchrom)
      except ValueError:
        if standchrom == 'X':
          standnum = 24
        elif standchrom == 'Y':
          standnum = 25
        elif standchrom == 'M':
          standnum = 26
      #Compare Chromosomes
      if testnum == standnum:
        #Same Chromosome; Compare Positions
        if int(test[1]) == int(standard[1]): 
          #Same Position; Compare INDEL status
          if (test[7][0:5]=='INDEL') == (standard[7][0:5]=='INDEL'):
            #Same INDEL status; Compare Alt
            if test[4] == standard[4]:
              pass
            else:
              fPos += 1
              temp = test[7][test[7].find('DP='):]
              coverage = int(temp[3: temp.find(';')])
              #if coverage > 0 and coverage <= 400:
               # covReposPos[int((coverage-1)/20)] += 1
             # else:
                #covReposPos[20] += 1 
              repos[(size,test[0], test[1], str(test[7][0:5]=='INDEL'))] += 1
              if int(test[1]) >= lastVariant:
                varDistance[(size, int(test[1])-lastVariant)] += 1
                lastVariant = int(test[1])
              else:
                lastVariant = 0              
            test = testFile.readline().split()
            standard = standardFile.readline().split()
          elif test[7][0:5]=='INDEL':
            #Test is an INDEL, thus "ahead"
            fNeg += 1
            temp = standard[7][standard[7].find('DP='):]
            coverage = int(temp[3: temp.find(';')])
            #if coverage > 0 and coverage <= 400:
            #  covReposNeg[int((coverage-1)/20)] += 1
            #else:
            #  covReposNeg[20] += 1            
            repos[(size, standard[0], standard[1], str(standard[7][0:5]=='INDEL'))] += 1
            if int(standard[1]) >= lastVariant:
              varDistance[(size, int(standard[1])-lastVariant)] += 1
              lastVariant = int(standard[1])
            else:
              lastVariant = 0
            standard = standardFile.readline().split()
          else:
            #Standard is an INDEL, thus "ahead"
            fPos += 1
            temp = test[7][test[7].find('DP='):]
            coverage = int(temp[3: temp.find(';')])
            #if coverage > 0 and coverage <= 400:
            #  covReposPos[int((coverage-1)/20)] += 1
            #else:
            #  covReposPos[20] += 1 
            repos[(size, test[0], test[1], str(test[7][0:5]=='INDEL'))] += 1
            if int(test[1]) >= lastVariant:
              varDistance[(size, int(test[1])-lastVariant)] += 1
              lastVariant = int(test[1])
            else:
              lastVariant = 0
            test = testFile.readline().split()
        elif int(test[1]) > int(standard[1]):
          #Test is "ahead"
          fNeg += 1
          temp = standard[7][standard[7].find('DP='):]
          coverage = int(temp[3: temp.find(';')])
          #if coverage > 0 and coverage <= 400:
          #  covReposNeg[int((coverage-1)/20)] += 1
          #else:
          #  covReposNeg[20] += 1 
          repos[(size, standard[0], standard[1], str(standard[7][0:5]=='INDEL'))] += 1
          if int(standard[1]) >= lastVariant:
            varDistance[(size, int(standard[1])-lastVariant)] += 1
            lastVariant = int(standard[1])
          else:
            lastVariant = 0
          standard = standardFile.readline().split()
        else:
          #Standard is "ahead"
          fPos += 1
          temp = test[7][test[7].find('DP='):]
          coverage = int(temp[3:temp.find(';')])
          #if coverage > 0 and coverage <= 400:
          #  covReposPos[int((coverage-1)/20)] += 1
          #else:
          #  covReposPos[20] += 1 
          repos[(size, test[0], test[1], str(test[7][0:5]=='INDEL'))] += 1
          if int(test[1]) >= lastVariant:
            varDistance[(size, int(test[1])-lastVariant)] += 1
            lastVariant = int(test[1])
          else:
            lastVariant = 0
          test = testFile.readline().split()   
      elif testnum > standnum:
        #Test is on a higher chromosome than standard
        fNeg += 1
        temp = standard[7][standard[7].find('DP='):]
        coverage = int(temp[3: temp.find(';')])
        #if coverage > 0 and coverage <= 400:
        #  covReposNeg[int((coverage-1)/20)] += 1
        #else:
        #  covReposNeg[20] += 1 
        repos[(size, standard[0], standard[1], str(standard[7][0:5]=='INDEL'))] += 1
        if int(standard[1]) >= lastVariant:
          varDistance[(size, int(standard[1])-lastVariant)] += 1
          lastVariant = int(standard[1])
        else:
          lastVariant = 0
        standard = standardFile.readline().split()
      else:
        #Standard is on a higher chromosome than test
        fPos += 1
        temp = test[7][test[7].find('DP='):]
        coverage = int(temp[3: temp.find(';')])
        #if coverage > 0 and coverage <= 400:
        #  covReposPos[int((coverage-1)/20)] += 1
        #else:
        #  covReposPos[20] += 1 
        repos[(size, test[0], test[1], str(test[7][0:5]=='INDEL'))] += 1
        if int(test[1]) >= lastVariant:
          varDistance[(size, int(test[1])-lastVariant)] += 1
          lastVariant = int(test[1])
        else:
          lastVariant = 0
        test = testFile.readline().split()
  
  #posOutput = str(size)
  #for i in covReposPos:
  #  posOutput += '\t' + str(i)
  #posOutput += '\n'
  #posOut.write(posOutput) 

  #negOutput = str(size)
  #for j in covReposNeg:
  #  negOutput += '\t' + str(j)
  #negOutput += '\n'
  #negOut.write(negOutput)

  testFile.close()
  standardFile.close()
  return fPos, fNeg
 
"""
Goes through all keys in the repositiory. For each member in the repository, calculates the percentage of samples that have an "error" at that point for each down sample size.
The output is: [samplesize] [#entries at that sample size] [# occurances <5% of files] [# occurances >= 5%  <10% files]... [ # occurances >= 95% <100%] [# occurances in 100%]
"""
def processRepository():
  #result = {}
  #downsamplesizes = sizes.keys()
  #for downsample in downsamplesizes:
  #  result.setdefault(downsample, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

  keyring = repos.keys()
  for key in keyring:
    percent = repos[key]/(sizes[key[0]])
    baroutput = str(key[0]) + "\t" + str(percent) + "\n"
    barchart.write(baroutput)

    #result[key[0]][0] += 1
    #result[key[0]][int(20*percent) + 1] += 1

  """
  resultlist = result.keys()
  for key in resultlist:
    baroutput = str(key) + '\t'
    barchart.write(baroutput),
    count = 0
    for block in result[key]:
      baroutput = str(block)
      count += 1
      if count < len(result[key]):
        baroutput += '\t'
      barchart.write(baroutput)
    barchart.write('\n')
    """

  varDistances = varDistance.keys()
  for key in varDistances:
    distanceoutput = str(key[0]) + '\t' + str(key[1]) + '\t' +  str(varDistance[key]) + '\n'
    distanceOut.write(distanceoutput)

args = parseArguments()
main(args)

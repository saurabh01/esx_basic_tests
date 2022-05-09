

"""

PathChecker.py -i file/dir -c ConfigFile [-o OutFile] [-a action]

If directory is passed or if OutFile is not mentioned;
 the input file will be over written during the edit.

Default Output file is the input file.

csv should be in the form.

"oldstring, newstring" for edit
 or
"oldlocation, newlocation" for move.

Caution: File may get re-written and users has to carefully handle the perforce files.

"""


from optparse import OptionParser
from subprocess import call
import os,sys,csv
import shutil

diction = {}

def getOptions():
    parser = OptionParser(usage=__doc__)
    parser.add_option('-i','--input',dest='input',help="Either directory or a file name to be processed[Mandatory if the action is Edit]")
    parser.add_option('-o','--output',dest='output', help="Name of the output file.Default is input file.")
    parser.add_option('-c','--config',dest='config', help="Config file.[Mandatory]")
    parser.add_option('-a','--action',dest='action', help="Action ( Edit or Move ).Default is edit")
    return parser.parse_args(sys.argv)


def csvtoHash(config):
   for col in csv.reader(open(config), delimiter=','):
      if (col[1] == "Current Location") or (col[1] == "old string"):
         pass
      else:
         diction[col[1]] = col[2]
   return 1;


def ProcessFile(INFILE,OUTFILE = None):
   if not OUTFILE :
      OUTFILE = INFILE
   tmpdata = data = open(INFILE).read()
   for key in diction:
      while (key in data):
         data = data.replace(key,diction[key])
   if tmpdata != data :
      try:
         call("p4 edit " + OUTFILE, shell=True)
      except:
         e = sys.exc_info()[1]
         print >>sys.stderr, "Migration failed:", e

   outfile = open(OUTFILE,'w')
   outfile.write(data)
   outfile.close()

def moveFiles ():
   for key in diction:
      destdir = os.path.dirname(diction[key])
      if (not os.path.exists(destdir)) and (not destdir in ("New Location","",None)):
          os.makedirs(destdir)
      try:
         call("p4 open " + key, shell=True)
         call("p4 move " + key + " " + diction[key], shell=True)
      except: # catch *all* exceptions
         e = sys.exc_info()[1]
         print >>sys.stderr, "Migration failed:", e
   return 1

if __name__ == "__main__":
    # Check for right options availability
    if ('-c' not in sys.argv):
        sys.argv.append('-h')
    options, args = getOptions()    
    inputFile = options.input or None
    outputFile =  options.output
    config = options.config
    action = options.action or None
 

    if  ((not os.path.exists(config)) or (not '.csv' in config.lower()[-4:])):
        print "A valid config file has to be passed and should be a .csv file"
        sys.exit(1)

    csvtoHash(config)
    
    if (action and (action == "Move")):
       moveFiles();
       sys.exit(1) # Success

    if (not inputFile):
	print "The input File shoule be mentioned for edit"
        sys.exit(0) 
    if not os.path.exists(inputFile):
       print "The config File "+inputFile + " doesn't exist in the machine"
       sys.exit(1);
    isFile = os.path.isfile(inputFile)
    isDir  = os.path.isdir(inputFile)
    if isDir:
       # Walk through directory and find all files 
       for directory, subdirectories, filenames in os.walk(inputFile):
          for filename in filenames:
             if ('.jar' in filename.lower()[-4:]): continue            
             print 'Processing file : ', filename
             filename = os.path.join(directory, filename)
             try:
                if outputFile:
                   ProcessFile(filename,outputFile)
                else:
                   ProcessFile(filename)
             except: # catch *all* exceptions
                e = sys.exc_info()[1]
                print >>sys.stderr, "Couldn't process "+ inputFile, e

    else:
        try:
            print 'Processing file : '+inputFile
            if outputFile:
               ProcessFile(inputFile,outputFile)
            else:
               ProcessFile(inputFile)
        except: # catch *all* exceptions
           e = sys.exc_info()[1]
           print >>sys.stderr, "Couldn't process "+ inputFile, e
    sys.exit(1)# success

# Sample program using etparse.py
#  - Raoul Veroy
import os
import sys
import argparse
import logging
import re
import subprocess
import pprint

from etparse import is_valid_op, is_heap_alloc_op, is_heap_op, parse_line, \
                    is_valid_version

def setup_logger( targetdir = ".",
                  filename = "sample_et.log",
                  logger_name = None,
                  debugflag = 0 ):
    assert(logger_name != None)
    # Set up main logger
    mylogger = logging.getLogger( logger_name )
    formatter = logging.Formatter( '[%(funcName)s] : %(message)s' )
    filehandler = logging.FileHandler( os.path.join( targetdir, filename ) , 'w' )
    if debugflag:
        mylogger.setLevel( logging.DEBUG )
        filehandler.setLevel( logging.DEBUG )
    else:
        filehandler.setLevel( logging.ERROR )
        mylogger.setLevel( logging.ERROR )
    filehandler.setFormatter( formatter )
    mylogger.addHandler( filehandler )
    return mylogger

def get_trace_fp( tracefile = None,
                  logger = None ):
    if not os.path.isfile( tracefile ) and not os.path.islink( tracefile ):
        # File does not exist
        logger.error( "Unable to open %s" % str(tracefile) )
        print "Unable to open %s" % str(tracefile)
        exit(21)
    bz2re = re.compile( "(.*)\.bz2$", re.IGNORECASE )
    gzre = re.compile( "(.*)\.gz$", re.IGNORECASE )
    bz2match = bz2re.search( tracefile )
    gzmatch = gzre.search( tracefile )
    if bz2match: 
        # bzip2 file
        fp = subprocess.Popen( [ "bzcat", tracefile ],
                               stdout = subprocess.PIPE,
                               stderr = subprocess.PIPE ).stdout
    elif gzmatch: 
        # gz file
        fp = subprocess.Popen( [ "zcat", tracefile ],
                               stdout = subprocess.PIPE,
                               stderr = subprocess.PIPE ).stdout
    else:
        fp = open( tracefile, "r")
    return fp

def process_input( fptr = None,
                   version = None,
                   stopline = None,
                   logger = None ):
    cur = 0
    pp = pprint.PrettyPrinter( indent = 4 )
    for x in fptr:
        rec = parse_line( line = x,
                          version = version,
                          logger = logger )
        cur = cur + 1
        pp.pprint( rec )
        if stopline > 0 and stopline == cur:
            break

def main_process( tgtpath = None,
                  stopline = None,
                  version = None,
                  logger = None,
                  debugflag = False # UNUSED
                  ):
    fptr = get_trace_fp( tracefile = tgtpath, logger = logger )
    version = 5
    process_input( fptr = fptr,
                   version = version,
                   stopline = stopline,
                   logger = logger )
    print "=====[ DONE ]========================================"
    exit(0)

def main():
    # Setup the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument( "source", help = "Source trace file." )
    parser.add_argument( "--logfile", help = "Logfile name." )
    parser.add_argument( "--outpickle", help = "Pickle output." )
    parser.add_argument( "--lines", default = 0, help = "Number of lines to read (default = 100. 0 = read all)." )
    parser.add_argument( "--version", default = 5, help = "ET version (default = 5)" )
    parser.add_argument( "--debug",
                         action = "store_true",
                         default = False,
                         help = "enable debug (default = False)" )
    args = parser.parse_args()

    # Get input filename
    tgtpath = args.source
    try:
        if not os.path.exists( tgtpath ):
            parser.error( tgtpath + " does not exist." )
    except:
        parser.error( "invalid path name : " + tgtpath )
    # Get logfile
    logfile = args.logfile
    logfile = "sample_et-" + os.path.basename(tgtpath) + ".log" if not logfile else logfile    
    #
    # Figure out the pickle args
    outpickle = args.outpickle
    outpickle = "sample_et-" + os.path.basename(tgtpath) + ".pickle" if not outpickle else outpickle    
    # 
    # Get the line option
    stopline = args.lines
    try:
        assert( stopline != None )
    except:
        parser.error( "Please supply a line number.")
    try:
        stopline = int(stopline)
        if stopline < 0:
            raise Exception("Invalid line number.")
    except:
        parser.error( "Please supply a valid line number. Percentages are"
                      " working just yet.")
    #
    # Get version
    version = args.version
    try:
        tmpver = int(version)
        version = tmpver
    except:
        if version == None:
            version = "<None>"
        parser.error( "Illegal version: " + version )
    # set debug flag
    debugflag = args.debug
    logger_name = 'sample_et'
    logger = setup_logger( filename = logfile,
                           logger_name = logger_name,
                           debugflag = debugflag )
    logger.debug("source: %s" % str(tgtpath))
    logger.debug("logfile: %s" % str(logfile))
    logger.debug("version: %d" % version)
    #
    # Main processing
    #
    main_process( tgtpath = tgtpath,
                  debugflag = debugflag,
                  version = version,
                  stopline = stopline,
                  logger = logger )

if __name__ == "__main__":
    main()

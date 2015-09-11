import sys
from optparse import OptionParser, OptionGroup
import pprint

version_list = [ 5 ]
_latestVersion = 5
# Exported names
heap_op_list = {}
valid_op_list = {}
# Version 5
_alloc_list_1 = [ "A", "I", "N", "P", "V", ]
heap_alloc_list = { 5 : _alloc_list_1, }
heap_op_list[5]  = heap_alloc_list[5] + [ "D", "U", ]
valid_op_list[5] = heap_op_list[5] + \
                   [ "M", "E", # method entry and exit
                     "T", "H", "X", # exception related
                     "R",  # root object
                     ]

# Setup logging
# We expect the logger to be passed in init of the class
logger = None
pp = pprint.PrettyPrinter( indent = 4 )

#
# Main processing
#
def is_valid_op( op = None, version = _latestVersion ):
    global valid_op_list
    assert( version in valid_op_list )
    return op in valid_op_list
        
def is_heap_op( op = None, version = _latestVersion ):
    global heap_op_list
    try:
        assert( version in version_list )
    except:
        print version
        print version_list
        exit(5)
    return op in heap_op_list[version]
        
def is_heap_alloc_op( op = None, version = _latestVersion ):
    global heap_alloc_list
    try:
        assert( version in version_list )
    except:
        print version
        print version_list
        exit(5)
    return op in heap_alloc_list[version]
        
def is_method_op( op = None, version = _latestVersion ):
    if op == "M" or op == "E":
        return True
    else:
        return False

def parse_line( line = None,
                version = _latestVersion,
                hashobj = None,
                hex2decflag = False,
                logger = None ):
    # Return a dictionary with keys:
    #    rectype - ALL
    #    objId - A,D,U,M,E,R
    #    threadId - A,U,M,E,R
    #    type - A
    #    size - A
    #    newTgtId - U
    #    oldTgtId - U
    assert( version )
    assert( line != None )
    if hashobj != None:
        hashobj.update(line)
    return __parse_line_nocheck( line = line,
                                 version = version,
                                 hex2decflag = hex2decflag,
                                 logger = logger )

def hex2dec( val ):
    try:
        retval = int(val, 16)
    except:
        return None
    return retval
    
def __parse_line_nocheck( line = None,
                          version = _latestVersion,
                          hex2decflag = False,
                          logger = None ):
    # VERSION 5:
    ret = {}
    if version == 5:
        a = line.split()
        if ( a[0] in heap_alloc_list[version] or
             a[0] == "D" or a[0] == "R" ):
             objId = hex2dec(a[1])
        else: # everything else
            objId = hex2dec(a[2])
        if (objId == None) or (type(objId) != type(1)):
            print "ERROR DEBUG:"
            print "line: %s" % str(line)
            print "objId: %s" % str(objId)
            exit(2000)
            return None
        if a[0] in heap_alloc_list[version]:
            ret["rectype"] = a[0]
            ret["objId"] = objId
            ret["size"] = hex2dec(a[2])
            ret["type"] = a[3]
            ret["site"] = hex2dec(a[4])
            ret["length"] = a[5]
            ret["threadId"] = hex2dec(a[6])
        elif a[0] == "D":
            ret["rectype"] = "D"
            ret["objId"] = objId
        elif a[0] == "U":
            ret["rectype"] = "U"
            ret["oldTgtId"] = hex2dec(a[1])
            ret["objId"] = objId
            ret["newTgtId"] = hex2dec(a[3])
            ret["fieldId"] = hex2dec(a[4])
            ret["threadId"] = hex2dec(a[5])
        elif a[0] == "M":
            ret["rectype"] = "M"
            ret["methodId"] = a[1]
            ret["objId"] = objId
            ret["threadId"] = hex2dec(a[3])
        elif a[0] == "E" or a[0] == "X":
            ret["rectype"] = a[0]
            ret["methodId"] = a[1]
            ret["objId"] = objId
            ret["threadId"] = hex2dec(a[3])
        elif a[0] == "T" or a[0] == "H":
            ret["rectype"] = a[0]
            ret["methodId"] = a[1]
            ret["objId"] = objId
            ret["exceptionId"] = a[3]
        elif a[0] == "R":
            ret["rectype"] = a[0]
            ret["objId"] = a[1]
            ret["threadId"] = hex2dec(a[2])
        else:
            print "Unknown record type: %s" % a[0]
            print "-------------------------------------"
            pp.pprint( a )
            raise ValueError( "Unknown record type: %s" % a[0] )
            # TODO Debug only
            # return None
            exit(-1)
    else:
        if logger != None:
            try:
                logger.error( "Unknown version: %d" % version )
            except:
                print "Error logging to supplied logger."
        raise ValueError( "Unknown version: %s" % str(version) )
    assert( ret != None )
    return ret

def is_valid_version( version = _latestVersion ):
    return version in version_list

class ETParserIter(object):
    def __init__( self, etp = None ):
        self.etp = etp

    def __iter__( self ):
        return self

    # raises StopIteration if empty
    def next( self ):
        try:
            data = self.etp.next()
        except StopIteration:
            raise StopIteration
        except:
            print "Unexpected exception:", sys.exc_info()[0]
            raise
        return data


__all__ = [ is_valid_op, is_heap_alloc_op, is_heap_op, parse_line,
            version_list, is_valid_version ]

if __name__ == "__main__":
    # TODO
    pass

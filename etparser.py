#!/usr/bin/env python
"""
Usage in python:

λ> from etparser import EventIter, parse_event
λ> with open('my-et.trace', 'r') as fp:
λ>   for event in EventIter(fp):
λ>     # analyze events ...
λ>     ...
λ> # Or:
λ> pprint(parse_event('V 1b4b 30 Ljava/lang/String; 0 0 85'))
{'allocType': 'V',
 'length': '0',
 'objID': '1b4b',
 'site': '0',
 'size': '30',
 'threadID': '85',
 'type': 'Ljava/lang/String;'}

This parser conforms to Version 5 of the Elephant Tracks
trace file format.
"""
import sys
from pprint import pprint

__all__ = ["parse_event", "EventIter"]

# Guarantees tuple of length num returned, else die:
def trysplit(line, num):
  splt = line.split()
  if len(splt) != num:
    print "Unable to parse '%s'" % (line.rstrip())
    print splt
    exit(0)
  return splt

# Make dictionary from line entry and expected keys in entry:
def dict_zip(line, keys):
  return dict(zip(keys, trysplit(line, len(keys))))

# Allocation event parser:
alloc_keys = ['objID', 'size', 'type', 'site', 'length', 'threadID']
def alloc(typ):
  def _alloc(l):
    d = dict_zip(l, alloc_keys)
    d.update({'allocType': typ})
    return d
  return _alloc

# Generate event parser expecting the given keys:
def event_parser(keys): return (lambda l: dict_zip(l, keys))

# Fields for each type of event (to be used as dictionary keys):
object_death_keys = ['objID'] # TODO: threadID, but it's not in '201.trace'
update_field_keys = ['oldTargetID', 'objID', 'newTargetID', 'fieldID', 'threadID']
method_entry_keys = ['methodID', 'receiverObjID', 'threadID']
method_exit_keys = ['methodID', 'receiverObjID', 'threadID']
exceptional_exit_keys = ['methodID', 'receiverObjID', 'exceptionID', 'threadID']
exception_keys = ['methodID', 'receiverID', 'exceptionObjID', 'threadID']
exception_handled_keys = ['methodID', 'receiverID', 'exceptionObjID', 'threadID']
root_object_keys = ['rootObjID', 'threadID']

# Map from 'ET Record Types' to corresponding parser function
_parse_event = {
    '#': lambda l: None
  , 'A': alloc('A') # Array alloc
  , 'I': alloc('I') # Initial heap alloc
  , 'N': alloc('N') # Alloc via new byte code
  , 'P': alloc('P') # Discovered after actual alloc
  , 'V': alloc('V') # VM object
  , 'D': event_parser(object_death_keys)
  , 'U': event_parser(update_field_keys)
  , 'M': event_parser(method_entry_keys)
  , 'E': event_parser(method_exit_keys)
  , 'X': event_parser(exceptional_exit_keys)
  , 'T': event_parser(exception_keys)
  , 'H': event_parser(exception_handled_keys)
  , 'R': event_parser(root_object_keys)
}

# Returns a python dictionary parsed from the given ET event in string / line format:
def parse_event(line):
  '''Parse the given line as an Elephant Tracks event.'''
  if len(line) == 0:
    return None
  try:
    parser = _parse_event[line[0]]
  except KeyError as e:
    print "Unknown event type for line '%s'" % (line,)
    exit(-1)
  return parser(line[1:])

# Iterator over lines of an ET trace (e.g. over lines from a file stream object):
class EventIter:
  def __init__(self, stream): self.stream = stream
  def __iter__(self): return self
  def next(self):
    d = None
    # Ignore empty lines and comment lines:
    while d is None:
      d = parse_event(self.stream.next())
    return d

if __name__ == '__main__':
  with open('201.trace', 'r') as fp:
    for e in EventIter(fp):
      pprint(e)


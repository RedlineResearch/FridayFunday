#!/usr/bin/env python
# -*- coding: utf-8 -*- 
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

__all__ = [ "parse_event", "EventIter", "is_valid_op", "is_heap_op"
          , "is_heap_alloc_op", "is_method_op" ]

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

# Generate event parser expecting the given keys:
def event_parser(keys): return (lambda l: dict_zip(l, keys))

# Fields for each type of event (to be used as dictionary keys):
alloc_keys = ['objID', 'size', 'type', 'site', 'length', 'threadID']
object_death_keys = ['objID'] # TODO: threadID, but it's not in '201.trace'
update_field_keys = ['oldTargetID', 'objID', 'newTargetID', 'fieldID', 'threadID']
method_entry_keys = ['objID', 'receiverObjID', 'threadID']
method_exit_keys = ['objID', 'receiverObjID', 'threadID']
exceptional_exit_keys = ['objID', 'receiverObjID', 'exceptionID', 'threadID']
exception_keys = ['objID', 'receiverID', 'exceptionObjID', 'threadID']
exception_handled_keys = ['objID', 'receiverID', 'exceptionObjID', 'threadID']
root_object_keys = ['objID', 'threadID']

# Map from 'ET Record Types' to corresponding parser function
_parse_event = {
    'A': event_parser(alloc_keys) # Array alloc
  , 'I': event_parser(alloc_keys) # Initial heap alloc
  , 'N': event_parser(alloc_keys) # Alloc via new byte code
  , 'P': event_parser(alloc_keys) # Discovered after actual alloc
  , 'V': event_parser(alloc_keys) # VM object
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
  if len(line) == 0 or line[0] == '#':
    return None
  try:
    parser = _parse_event[line[0]]
  except KeyError as e:
    print "Unknown event type for line '%s'" % (line,)
    exit(-1)
  d = parser(line[1:])
  d.update({'rectype': line[0]})
  return d

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

# Event helper functions:
def is_valid_op(op):      return op in _parse_event.keys()
def is_heap_op(op):       return op in list('AINPVDU')
def is_heap_alloc_op(op): return op in list('AINPV')
def is_method_op(op):     return op in list('ME')

if __name__ == '__main__':
  with open('test1.trace', 'r') as fp:
    for e in EventIter(fp):
      pprint(e)


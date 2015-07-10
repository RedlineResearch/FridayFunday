#!/usr/bin/env python
from etparse import is_valid_op, is_heap_alloc_op, is_heap_op, parse_line, \
                    is_valid_version
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

heap = {}
i = 0

with open('201.trace', 'r') as fp:
  for line in fp:
    d = parse_line(line)
    objId = d['objId']
    if is_heap_alloc_op(d['rectype']):
      i += 1
      heap[d['objId']] = {'type': d['type'], 'fields': {}}
    elif d['rectype'] == 'U':
      if objId > 0 and heap.has_key(objId):
        heap[objId]['fields'][d['fieldId']] = d['newTgtId']
    elif d['rectype'] == 'D':
      del heap[objId]

    if i == 10000:
      pp.pprint(heap)
      break



#!/usr/bin/env python
# -*- coding: utf-8 -*-
#elephant tracks to datalog format
from etparser import is_heap_alloc_op, is_heap_op
from etparser import parse_event as parse_line
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

heap = {}
i = 0

class ObjectModel:
  def __init__(self, object_id, ty):
    self.object_id = object_id
    self.ty = ty
    self.fields = {} #Field ID -> (Creation Time, ObjectID)
def rulegen(obj_id, old_target, creation_time, update_count):
    print "pointsTo('A%s','A%s',%d,%d)"%(obj_id, old_target, creation_time, update_count)
update_count = 0 #Zero is reserved
ty2index = {}
next_type_index = 1
min_object_id = 1
max_object_id = -1
with open('test1.trace', 'r') as fp:
    for line in fp:
        d = parse_line(line)
        obj_id = d['objID']

        if (obj_id > max_object_id):
          max_object_id = obj_id

        if is_heap_alloc_op(d['rectype']):
            i += 1
            ty = d['type']
            heap[obj_id] = ObjectModel(obj_id, ty)

            if (ty not in ty2index):
               ty2index[ty] = next_type_index
               next_type_index += 1

        elif d['rectype'] == 'U':
            update_count += 1
            if obj_id > 0 and heap.has_key(obj_id):
                o_model = heap[obj_id]
                field_id = d['fieldID']

                new_target = d['newTargetID']

                if (field_id in o_model.fields):
                    (creation_time, old_target) = o_model.fields[field_id]
                    rulegen(obj_id, old_target, creation_time, update_count)

                o_model.fields[field_id] = (update_count, new_target)

        elif d['rectype'] == 'D':
            o_model = heap[obj_id]
            for (creation_time, neighbor) in o_model.fields.values():
                rulegen(obj_id, neighbor, creation_time, update_count)
            del heap[obj_id]

        if i == 10000:
            break


print "\n//Processing immortals"
for o_model in heap.values():
    for (creation_time, neighbor) in o_model.fields.values():
        rulegen(o_model.object_id, neighbor, creation_time, update_count)

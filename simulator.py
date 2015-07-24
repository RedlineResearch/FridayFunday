#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from etparser import is_heap_alloc_op, is_heap_op
from etparser import parse_event as parse_line
from pprint import PrettyPrinter
from z3 import *
pp = PrettyPrinter(indent=2)

heap = {}
i = 0

class ObjectModel:
  def __init__(self, object_id, ty):
    self.object_id = object_id
    self.ty = ty
    self.fields = {} #Field ID -> (Creation Time, ObjectID)

solver = Solver()
x = Int('x')
y = Int('y')
z = Int('z')
start = Int('start')
end = Int('end')
t = Int('t')
type_array = Array('type_array', IntSort(), IntSort())

# interval_pointsat :: Int -> Int -> Int -> Int -> Bool
interval_pointsat = Function('interval_pointsat', IntSort(), IntSort(), IntSort(), IntSort(), BoolSort())

# instant_pointsat :: Int -> Int -> Int -> Bool
instant_pointsat = Function('instant_pointsat', IntSort(), IntSort(), IntSort(), BoolSort())

# type_function :: Int -> Int
type_function = Function('type_function', IntSort(), IntSort())

# ∀ (x,y,start,end,t), (  t >= start && t <= end
#                      && interval_poinsat(x,y,start,end)
#                      ) ⇒ instant_pointsat(x,y,t)
_interval_condtn = And(t >= start, t <= end, interval_pointsat(x, y, start, end))
_interval_implies = Implies(_interval_condtn, instant_pointsat(x, y, t))
interval_to_instant = ForAll([x, y, start, end, t], _interval_implies)

solver.add(interval_to_instant)

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
            
            # Tell solver new heap alloc has the given type
            solver.add(type_function(obj_id) == ty2index[ty])
 
        elif d['rectype'] == 'U':
            update_count += 1
            if obj_id > 0 and heap.has_key(obj_id):
                o_model = heap[obj_id]
                field_id = d['fieldID']

                new_target = d['newTargetID']

                if (field_id in o_model.fields):
                    (creation_time, old_target) = o_model.fields[field_id]

                    solver.add(interval_pointsat(obj_id, old_target, creation_time, update_count))

                o_model.fields[field_id] = (update_count, new_target)

        elif d['rectype'] == 'D':
            o_model = heap[obj_id]
            for (creation_time, neighbor) in o_model.fields.values():
                solver.add(interval_pointsat(obj_id, neighbor, creation_time, update_count))
            del heap[obj_id]

        if i == 10000:
            pp.pprint(heap)
            break



for o_model in heap.values():
    for (creation_time, neighbor) in o_model.fields.values():
        solver.add(interval_pointsat(obj_id, neighbor, creation_time, update_count))


exclude_undefined = ForAll([x,y, start, end], Implies(type_function(x) == 0, And([instant_pointsat(x, y, start) == False, interval_pointsat(x, y, start, end) == False])))

null_typing = ForAll([x], Implies( Or([x < min_object_id, x > max_object_id]), type_function(x) == 0))

solver.add(null_typing)
solver.add(exclude_undefined)

# PointsAt(ObjectA, ObjectB, StartTime, EndTime) 
# Type(Object, Ty)
# ~(Exists x, y, z, t1
#     s.t.  Type(LLN, y), Type(LLN, x), Type(LLN, z),
#            instant_pointsat(y, z, t) && instant_pointsat(x, z, t)) 

test_object_index = ty2index["LTestObject;"]

solver.add(Exists([x,y,z,t], And([instant_pointsat(x, z, t),
                      instant_pointsat(y, z, t),
                      type_function(x) == test_object_index,
                      type_function(y) == test_object_index,
                      type_function(z) == test_object_index,
                      t <= update_count,
                      t >= 1])) )


print solver.check()

print solver.model()

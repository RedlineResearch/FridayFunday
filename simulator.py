#!/usr/bin/env python
from etparse import is_valid_op, is_heap_alloc_op, is_heap_op, parse_line, \
                    is_valid_version
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


interval_pointsat = Function('interval_pointsat', IntSort(), IntSort(), IntSort(), IntSort(), BoolSort())
instant_pointsat = Function('instant_pointsat', IntSort(), IntSort(), IntSort(), BoolSort())

type_function = Function('type_function', IntSort(), IntSort())

interval_to_instant = ForAll([x, y, start, end, t] , Implies( And(t >= start,  t <= end, interval_pointsat(x, y, start, end)), instant_pointsat(x, y, t))) 

solver.add(interval_to_instant)

update_count = 0
ty2index = {}
next_type_index = 0
with open('test1.trace', 'r') as fp:
    for line in fp:
        d = parse_line(line)
        obj_id = d['objId']
        if is_heap_alloc_op(d['rectype']):
            i += 1
	    ty = d['type']
            heap[obj_id] =  ObjectModel(obj_id, ty)

            if (ty not in ty2index):
               ty2index[ty] = next_type_index
               next_type_index += 1
            
            solver.add(type_function(obj_id) == ty2index[ty])            	    
 
        elif d['rectype'] == 'U':
            update_count += 1
            if obj_id > 0 and heap.has_key(obj_id):
                o_model = heap[obj_id]
                field_id = d['fieldId']

                new_target = d['newTgtId']

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
                      type_function(z) == test_object_index])) )




print solver.check()

print solver.model()

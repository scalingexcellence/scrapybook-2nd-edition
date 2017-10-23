#!/usr/bin/env python

import os
import sys

from model import Model
from view import View

model = Model()
properties = int(sys.argv[1])
per_index = 30

if not os.path.exists('properties'):
    os.mkdir('properties')

for pid in xrange(0, properties):
    item = model.get_item(pid)

    f = open("properties/property_%06d.html" % pid, "w")
    f.write(View.render_property(item))
    f.close()

indices = (properties + per_index - 1) / per_index
for page in xrange(0, indices):

    np = "index_%05d.html" % (page+1)

    start = per_index * page
    end = min(per_index * (page + 1), properties)

    index = {
        'page': page,
        'nextp': None if page >= (indices-1) else np,
        'items': model.get_items(xrange(start, end))
    }

    f = open("properties/index_%05d.html" % page, "w")
    f.write(View.render_index(index))
    f.close()

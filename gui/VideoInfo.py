#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import sys
import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")
import gst
d = gst.parse_launch("filesrc name=source ! decodebin2 ! fakesink")
source = d.get_by_name("source")
source.set_property("location", sys.argv[1])
d.set_state(gst.STATE_PLAYING)
d.get_state()
format = gst.Format(gst.FORMAT_TIME)
duration = d.query_duration(format)[0]
d.set_state(gst.STATE_NULL)

import datetime
delta = datetime.timedelta(seconds=(duration / gst.SECOND))
print delta

# -*- coding: utf-8 -*-

# Increase the value below, to show smaller squares and more cards
# Decrease to show bigger squares
maxCountX = 50

# Don't change stuff below this line
import time

import aqt
from aqt.qt import *
from aqt import mw

from anki.stats import CollectionStats
from anki.hooks import wrap, addHook

import cardheatmaphtml
import json

def getIntervalData(info):
    ids_and_ivl = None

    if info.wholeCollection:
        ids_and_ivl = mw.col.db.all("select id, ivl from cards")
    else:
        ids_and_ivl = mw.col.db.all("select id, ivl from cards where did = %s" % info.col.conf["activeDecks"][0])

    if not ids_and_ivl:
        return None

    data = list()
    index = 0

    for entry in ids_and_ivl:
        data.append({"id": entry[0], "ivl": entry[1], "y": index // maxCountX, "x": index % maxCountX})
        index = index + 1

    return data

def generateReport(data):
    # total width is 550px

    count = len(data)
    widthHeight = 500/maxCountX
    height = ((count // maxCountX) + 1) * widthHeight
    return cardheatmaphtml.heatmap_boilerplate + (cardheatmaphtml.heatmap_script % (json.dumps(data), widthHeight, height)) + cardheatmaphtml.heatmap_div

def injectHeatmapGraph(self, _old):
    """Wraps dueGraph and adds our heatmap to the stats screen"""
    #self is anki.stats.CollectionStats
    
    ret = _old(self)
    data = getIntervalData(self);

    if not data: # no cards found
        tooltip("No cards found to show on heatmap")
        return ret

    report = generateReport(data)
    html = report + ret

    return html

CollectionStats.dueGraph = wrap(CollectionStats.dueGraph, injectHeatmapGraph, "around")
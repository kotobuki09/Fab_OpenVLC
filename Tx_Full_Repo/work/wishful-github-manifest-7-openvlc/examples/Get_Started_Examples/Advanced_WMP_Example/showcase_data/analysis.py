#!/usr/bin/env python3
'''Utilities for analysis of Metamac log files.
'''

__author__ = "Pierluigi Gallo, Domenico Garlisi"
__copyright__ = "Copyright (c) 2016, CNIT"
__version__ = "0.1.0"
__email__ = "domenico.garlisi@cnit.it"

import csv
from math import *
import re
from glob import glob
import tempfile
from PIL import Image, ImageDraw, ImageFont
import os
import os.path

import numpy as np
import matplotlib.pyplot as plt

def parse_value(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s

class Log:
    def __init__(self, path, slot_time=2200, tsf_threshold=200000):
        self.path = path
        self.time_offset = 0.0
        self.slot_offset = 0
        m = re.search(r'alix\d+', path)
        if m:
            self.node = m.group()
        else:
            self.node = 'unknown'
        with open(path) as f:
            self.header = f.readline().strip().split(',')
            f.seek(0)
            reader = csv.DictReader(f)
            self.entries = [{k: parse_value(v) for k, v in r.items()} for r in reader if None not in r.values()]
        self.protocols = self.header[self.header.index('protocol')+1:]

        self.first_jump = len(self.entries)
        self.tsf_segments = []
        if len(self.entries) > 0:
            current_segment = [self.entries[0]["tsf_time"]]
            prev = current_segment[0]
            for i, entry in enumerate(self.entries):
                if abs(entry["tsf_time"] - prev) > tsf_threshold:
                    if self.first_jump > i:
                        self.first_jump = i
                    self.tsf_segments.append(current_segment)
                    current_segment = []
                if entry["tsf_time"] != prev:
                    current_segment.append(entry["tsf_time"])
                    prev = entry["tsf_time"]
            self.tsf_segments.append(current_segment)
            self.tsf_jumps = len(self.tsf_segments) > 1
        else:
            self.tsf_jumps = False

        current_read = self.entries[0]["read_num"]
        for i in range(len(self.entries)):
            if self.entries[i]["read_num"] != current_read:
                j = i - 1
                while j >= 0 and self.entries[j]["read_num"] == current_read:
                    self.entries[j]["tsf_interp"] = self.entries[j]["tsf_time"] - slot_time * (i - j - 1)
                    j -= 1
                current_read = self.entries[i]["read_num"]
        j = len(self.entries) - 1
        while j >= 0 and self.entries[j]["read_num"] == current_read:
            self.entries[j]["tsf_interp"] = self.entries[j]["tsf_time"] - slot_time * (len(self.entries) - j - 1)
            j -= 1

    def print_tsf_segments(self):
        for segment in self.tsf_segments:
            if len(segment) == 1:
                print(segment[0])
            elif len(segment) == 2:
                print(segment[0])
                print(segment[1])
            else:
                print(segment[0])
                print('...')
                print(segment[-1])

    def slot_num(self, num, hi=None):
        if hi is None:
            hi = len(self.entries) - 1
        lo = 0
        while lo < hi:
            mid = (lo + hi) >> 1
            if self.entries[mid]["slot_num"] < num:
                lo = mid + 1
            else:
                hi = mid
        if lo == hi and self.entries[lo]["slot_num"] == num:
            return self.entries[lo]
        return None

    def success_rate(self):
        transmissions = 0
        successes = 0
        for entry in self.entries:
            if entry["transmitted"] == 1:
                transmissions += 1
                if entry["transmit_success"] == 1:
                    successes += 1
        return float(successes) / transmissions

class Experiment:
    def __init__(self, globpattern, access_point=None, slot_time=2200, tsf_threshold=200000):
        self.access_point = access_point
        self.slot_time = slot_time
        self.logs = [Log(p, slot_time=slot_time, tsf_threshold=tsf_threshold) for p in glob(globpattern)]
        if len(self.logs) == 0:
            raise Exception('No logs found')
        self.tsf_jumps = False
        for log in self.logs:
            self.tsf_jumps |= log.tsf_jumps

        if self.access_point is None:
            baseline = self.logs[0]
        else:
            baseline = next(l for l in self.logs if l.node == self.access_point)

        for log in self.logs:
            total = 0.0
            count = 0
            for entry in baseline.entries[:baseline.first_jump]:
                slot = log.slot_num(entry["slot_num"], log.first_jump - 1)
                if slot is not None:
                    total += slot["tsf_interp"] - entry["tsf_interp"]
                    count += 1
            log.time_offset = total / count
            log.slot_offset = int(round(log.time_offset / slot_time))

    def tdma_assign_for_slot(self, slot):
        m = re.match(r'TDMA \(slot (\d+)\)', slot['protocol'])
        if not m:
            raise Exception('Unexpected naming convention for TDMA protocol.')
        proto = m.group(1)
        return int(proto)

    def plot_tdma(self, modulo=None, collisions=True, xlim=None, slotmax=2<<32, add_offset=0, saveto=None):
        if modulo is None:
            modulo = len(self.logs)
        if self.tsf_jumps:
            print("TSF jump behavior present!")
        #for log in logs:
        #    interpolate_tsf(log)
        symbols = ['bo', 'ro', 'go', 'yo']
        assert(len(symbols) >= len(self.logs))

        x_max = 0.0
        fig = plt.figure()
        ax = plt.subplot(111)
        for i, log in enumerate(self.logs):
            nudge = .5 * (i + 1) / (len(self.logs) + 1)
            x = [(r["slot_num"] + log.slot_offset) * (self.slot_time * 1e-6) for r in log.entries if (r["slot_num"] + log.slot_offset <= slotmax) and r["transmitted"] == 1 and r["transmit_success"] == 1]
            y = [((r["slot_num"] + log.slot_offset + add_offset) % modulo) - .25 + nudge for r in log.entries if (r["slot_num"] + log.slot_offset <= slotmax) and r["transmitted"] == 1 and r["transmit_success"] == 1]
            ax.plot(x, y, symbols[i], label=log.node)
            if len(x) > 0:
                x_max = max(x_max, max(x))
            if collisions:
                x = [(r["slot_num"] + log.slot_offset) * (self.slot_time * 1e-6) for r in log.entries if (r["slot_num"] + log.slot_offset <= slotmax) and r["transmitted"] == 1 and r["transmit_success"] == 0]
                y = [((r["slot_num"] + log.slot_offset + add_offset) % modulo) - .25 + nudge for r in log.entries if (r["slot_num"] + log.slot_offset <= slotmax) and r["transmitted"] == 1 and r["transmit_success"] == 0]
                ax.plot(x, y, symbols[i], mfc='none', mec=symbols[i][0], label=None)

        box = ax.get_position()
        ax.set_position([box.x0, 1.0 - (1.0 - box.y0) * .9, box.width, box.height * .9])
        plt.figlegend([l for l in ax.lines if l.get_markerfacecolor() != 'none'], [l.node for l in self.logs], loc = 'lower center', bbox_to_anchor = (0,0,1,1),
            ncol=2, labelspacing=0.)
        if xlim is not None:
            ax.set_xlim(xlim)
        ax.grid(True)
        ax.set_xlabel('time (s)')
        ax.set_ylabel('TDMA slot assignment')
        ax.set_ylim([-0.5, 3.5])
        plt.yticks([0, 1, 2, 3])
        if saveto is None:
            plt.show()
        else:
            plt.savefig(saveto)

    def plot_weights(self, xlim=None, slotmax=2<<32, logscale=False, saveto=None):
        for log in self.logs:
            assert(log.protocols == self.logs[0].protocols)
        if len(self.logs) == 4:
            fig, axarr = plt.subplots(2, 2, sharex='col', sharey='row')
            axes = [axarr[0, 0], axarr[1, 0], axarr[1, 1], axarr[0, 1]]
            symbols = ["b", "r", "g", "y", "k"]
        else:
            raise Exception('Unimplemented number of nodes.')

        for log, ax in zip(self.logs, axes):
            for i, proto in enumerate(log.protocols):
                x = [(r["slot_num"] + log.slot_offset) * (self.slot_time * 1e-6) for r in log.entries if (r["slot_num"] + log.slot_offset <= slotmax)]
                y = [r[proto] for r in log.entries if (r["slot_num"] + log.slot_offset <= slotmax)]
                if logscale:
                    ax.semilogy(x, y, symbols[i], label=proto)
                else:
                    ax.plot(x, y, symbols[i], label=proto)
            ax.set_title(log.node)
            if logscale:
                pass
                #ax.set_ylim([1e-20, 1.0])
            else:
                ax.set_ylim([0.0, 1.0])
            if xlim is not None:
                ax.set_xlim(xlim)
            if log == self.logs[0] or log == self.logs[1]:
                ax.set_ylabel('Protocol weight')
            if log == self.logs[1] or log == self.logs[2]:
                ax.set_xlabel('time (s)')
            ax.grid(True)
            box = ax.get_position()
            newbox = [box.x0, 1.0 - (1.0 - box.y0) * .9, box.width, box.height * .9]
            print(box)
            print(newbox)
            ax.set_position(newbox)
        plt.figlegend( ax.lines, log.protocols, loc = 'lower center', bbox_to_anchor = (0,0,1,1),
            ncol=2, labelspacing=0.)
        if saveto is None:
            plt.show()
        else:
            plt.savefig(saveto)

    def animate(self, start_slot_num, end_slot_num, naming, view_width=136, logscale=False):
        name_template = os.path.splitext(naming)[0] + '{0}' + os.path.splitext(naming)[1]
        font = ImageFont.truetype('/usr/share/fonts/TTF/Inconsolata-Regular.ttf', 30)
        xmit_attempted = 0
        xmit_succeeded = 0
        slots_queued = 0
        slots_succeeded = 0
        for slot_num in range(0, max(l.entries[-1]["slot_num"] for l in self.logs)):
            slot_queued = False
            slot_succeeded = False
            for log in self.logs:
                slot = log.slot_num(slot_num - log.slot_offset)
                if slot is not None:
                    xmit_attempted += slot["transmitted"]
                    xmit_succeeded += slot["transmitted"] & slot["transmit_success"]
                    slot_queued = slot_queued or (slot["packet_queued"] == 1)
                    slot_succeeded = slot_succeeded or (slot["transmitted"] & slot["transmit_success"] == 1)
            if slot_queued:
                slots_queued += 1
            if slot_succeeded:
                slots_succeeded += 1
            if slot_num >= start_slot_num and slot_num <= end_slot_num:
                tdma_fig = tempfile.mktemp() + ".png"
                self.plot_tdma(xlim=[(slot_num - (view_width / 2)) * .0022, (slot_num + (view_width / 2)) * .0022], slotmax=slot_num, saveto=tdma_fig)
                weights_fig = tempfile.mktemp() + ".png"
                self.plot_weights(xlim=[(slot_num - (view_width / 2)) * .0022, (slot_num + (view_width / 2)) * .0022], logscale=logscale, slotmax=slot_num, saveto=weights_fig)
                combined = Image.new("RGB", (1600, 800), (255, 255, 255))
                combined.paste(Image.open(tdma_fig, 'r'), (0, 0))
                combined.paste(Image.open(weights_fig, 'r'), (800, 0))
                draw = ImageDraw.Draw(combined)
                draw.text((60, 650), 'Slot number: ' + str(slot_num), font=font, fill=(0,0,0))
                draw.text((60, 700), 'Time: {:.2f}ms'.format(slot_num * .0022), font=font, fill=(0,0,0))
                msg = 'Channel utilization: {:.4f}%'.format(slots_succeeded / slots_queued) if slots_queued > 0 else 'Channel utilization: N/A'
                draw.text((60, 750), msg, font=font, fill=(0,0,0))
                draw.text((860, 650), 'Total transmissions attempted: ' + str(xmit_attempted), font=font, fill=(0,0,0))
                draw.text((860, 700), 'Total transmissions succeeded: ' + str(xmit_succeeded), font=font, fill=(0,0,0))
                msg = 'Transmission success rate: {:.4f}%'.format(xmit_succeeded / xmit_attempted) if xmit_attempted > 0 else 'Transmission success rate: N/A'
                draw.text((860, 750), msg, font=font, fill=(0,0,0))
                combined.save(name_template.format(str(slot_num).zfill(5)))
                combined.close()
                os.remove(tdma_fig)
                os.remove(weights_fig)


def count(logs, *predicates):
    count = 0
    for log in logs:
        for entry in log:
            satisfies = True
            for predicate in predicates:
                if entry[predicate] != 1:
                    satisfies = False
                    break
            if satisfies:
                count += 1
    return count

def load_log(path):
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        return [{k: parse_value(v) for k, v in r.items()} for r in reader if None not in r.values()]

def invalid_offsets(log, modulo):
    slots = []
    off = {}
    t = [r for r in log if r['transmitted']]
    for i in range(len(t) - 1):
        diff = (t[i+1]['slot_num'] - t[i]['slot_num']) % modulo
        if diff != 0:
            slots.append(t[i+1])
            if diff in off:
                off[diff] += 1
            else:
                off[diff] = 1
    return slots, off, len(t) - 1

def show_invalid_offsets(log, modulo):
    slots, off, total = invalid_offsets(log, modulo)
    invalid = len(slots)
    print("{} invalid offsets out of {} ({})".format(invalid, total, float(invalid) / total))
    print(off)

def run_invalid_offsets(path, modulo):
    log = load_log(path)
    show_invalid_offsets(log, modulo)

def invalid_slot_nums(log, modulo):
    slots, off, total = invalid_offsets(log, modulo)
    return [s['slot_num'] for s in slots]

def run_invalid_slot_nums(path, modulo):
    log = load_log(path)
    return invalid_slot_nums(log, modulo)


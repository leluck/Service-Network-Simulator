# Copyright (c) 2012 Johannes Bendler
# Licensed under the MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining 
# a copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
# IN THE SOFTWARE.

import numpy

class Empty:
    '''Defines a bouncer, which does not decline jobs at all but is
    able to calculate base values and tendencies for comparison plots.
    '''
    
    def __init__(self):
        self.horizon = 50
        self.trace = []
    
    def reset(self):
        self.trace = []
    
    def _currentLoad(self, loadTrace, t):
        horizon = self.horizon
        if len(loadTrace) < self.horizon + 1:
            horizon = len(loadTrace) - 1
        
        loadList = []
        for offset in range(0, horizon - 1):
            loadList.append(loadTrace[t - offset]['activeServices'] - loadTrace[t - (offset + 1)]['activeServices'])
        
        loadValue = 0.0
        try:
            loadValue = sum([float(x) for x in loadList]) / float(len(loadList))
        except Exception:
            loadValue = 0.0

        return loadValue
            
    def filterJobs(self, jobs, loadTrace):
        if not len(loadTrace):
            # Accept all jobs if no load data is present
            return jobs, set()
        
        horizon = self.horizon
        if len(loadTrace) < self.horizon + 1:
            horizon = len(loadTrace) - 1
        
        current = len(loadTrace) - 1
        deltaList = []
        for offset in range(0, horizon - 1):
            deltaList.append(self._currentLoad(loadTrace, current) - self._currentLoad(loadTrace, current - offset))
                
        basevalue = self._currentLoad(loadTrace, current)
        tendency = sum([float(x) for x in deltaList]) / float(len(deltaList)) if len(deltaList) else 0.0
        tendency -= basevalue
                
        self.trace.append('%03d %.2f, %.2f %d' % (current, basevalue, tendency, len(jobs)))
        
        return jobs, set()
    
    def exportTrace(self, filename):
        with open(filename, 'w') as outfile:
            for i in self.trace:
                outfile.write('%s\n' % (i))

class Bouncer:
    '''Defines a bouncer, wich splits the set of given newly generated
    jobs into a set of accepted and a set of declined jobs by watching
    the system state of the past and current iterations. Can implement
    a reinforcement learning approach, if desired.
    '''
    
    def __init__(self):
        self.horizon = 20
        self.reset()
    
    def reset(self):
        self.trace = []
        self.tendency = []
        self.derivative = []
        self.fullTrace = []
    
    def _load(self, t):
        try:
            maxRes = 0.0
            for resPool in self.fullTrace[t]['resources']:
                for resource in self.fullTrace[t]['resources'][resPool]:
                    if self.fullTrace[t]['resources'][resPool][resource] > maxRes:
                        maxRes = self.fullTrace[t]['resources'][resPool][resource]

            return float(self.fullTrace[t]['activeServices']) * maxRes
        except IndexError:
            return 0.0
    
    def _weightedTendency(self):
        if not len(self.fullTrace):
            return 0.0
        
        if len(self.fullTrace) < self.horizon + 1:
            horizon = len(self.fullTrace) - 1
        else:
            horizon = self.horizon
        
        lastIndex = len(self.fullTrace) - 1
        weightedDiffs = []
        for offset in range(1, horizon):
            weightedDiffs.append((self._load(lastIndex) - self._load(lastIndex - (offset))) / float(offset))
        
        return sum(weightedDiffs) / float(horizon)
    
    def _smoothTendency(self, horizon):
        if len(self.tendency) < horizon + 1:
            horizon = len(self.tendency) - 1
        
        # Smoothes the last value based on the given horizon in-place!
        accumulated = float(self.tendency[-1])
        for offset in range(1, horizon + 1):
            accumulated += float(self.tendency[-offset])
        self.tendency[-1] = accumulated / float(horizon)
            
    def filterJobs(self, jobs, loadData):
        self.fullTrace = loadData
        
        if len(self.fullTrace) < 2:
            # Accept all jobs if not enough load data is present
            self.tendency.append(0.0)
            return jobs, set()
        
        lastIndex = len(self.fullTrace) - 1
        basevalue = self._load(lastIndex)
        self.tendency.append(self._weightedTendency())
        self._smoothTendency(self.horizon)
        tendency = self.tendency[-1]
        self.derivative.append(self.deriveCurrent())
        derivative = self.derivative[-1]
        
        self.trace.append('%03d %.2f, %.2f %d %.2f' % (lastIndex, basevalue, tendency * 50, len(jobs), derivative))
        
        if len(jobs) == 0:
            # Return if the set of new jobs is empty
            # This has to happen this late, because the
            # trace entry (self.trace.append(...)) must
            # not be missing, even if its values are zero.
            return jobs, set()
        
        orderedJobs = list(jobs)
        orderedJobs.sort(key = lambda job: job.identifier)
        
        maxDervInHorizon = max(self.derivative[-self.horizon:])
        
        pivot = 0
        if derivative > 0:
            # System load is increasing, we should think
            # about declining some of the new jobs dependent
            # on the slope of our tendency ( = derivative).
            quota = derivative / maxDervInHorizon
            pivot = int(quota * len(jobs))
        else:
            pivot = len(jobs)
        
        # Return set of accepted jobs and set of declined jobs.
        return set(orderedJobs[:pivot]), set(orderedJobs[pivot:])
    
    def deriveCurrent(self):
        hist = self.horizon
        if len(self.tendency) < hist + 1:
            hist = len(self.tendency) - 1
            if hist < 1:
                return 0.0
        
        x = [(len(self.tendency) - 1) - (hist - i) for i in range(hist)]
        y = [self.tendency[(len(self.tendency) - 1) - (hist - i)] for i in range(hist)]
        
        coeffs = numpy.polyfit(x, y, deg = 1)
        
        h = 0.001
        e = 1e-08
        reg = numpy.poly1d(coeffs)
        ref = (numpy.polyval(reg, [self.tendency[-1] + h])[0] - numpy.polyval(reg, self.tendency[-1:])[0]) / h
        while True:
            h /= 2.0
            new = (numpy.polyval(reg, [self.tendency[-1] + h])[0] - numpy.polyval(reg, self.tendency[-1:])[0]) / h
            diff = abs(ref - new)
            ref = new
            if diff < e: break
        return ref
    
    def exportTrace(self, filename):
        with open(filename, 'w') as outfile:
            for i in self.trace:
                outfile.write('%s\n' % (i))
    
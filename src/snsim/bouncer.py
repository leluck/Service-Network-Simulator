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
        
        if len(jobs) == 0:
            # Return if the set of new jobs is empty
            # This has to happen this late, because the
            # trace entry (self.trace.append(...)) should 
            # not be missing.
            return jobs, set()
        
        orderedJobs = list(jobs)
        orderedJobs.sort(key = lambda job: job.identifier)
        
        pivot = 0
        if tendency > 0:
            if basevalue > 0:
                pivot = 0
            else:
                pivot = len(jobs)
        else:
            pivot = len(jobs)
        
        return set(orderedJobs[:pivot]), set(orderedJobs[pivot:])
    
    def exportTrace(self, filename):
        with open(filename, 'w') as outfile:
            for i in self.trace:
                outfile.write('%s\n' % (i))
    
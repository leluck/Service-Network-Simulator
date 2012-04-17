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

class Bouncer:
    '''Defines a bouncer, wich splits the set of given newly generated
    jobs into a set of accepted and a set of declined jobs by watching
    the system state of the past and current iterations. Can implement
    a reinforcement learning approach, if desired.
    '''
    
    def __init__(self):
        self.horizon = 50
        self.lastThreshold = 0
    
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
            return jobs, []
        
        horizon = self.horizon
        if len(loadTrace) < self.horizon + 1:
            horizon = len(loadTrace) - 1
        
        current = len(loadTrace) - 1
        deltaList = []
        for offset in range(0, horizon - 1):
            deltaList.append(self._currentLoad(loadTrace, current - offset) - self._currentLoad(loadTrace, current - (offset + 1)))
                
        basevalue = self._currentLoad(loadTrace, current)
        tendency = sum([float(x) for x in deltaList])
                
        print('%03d %.2f, %.2f %d' % (current, basevalue, tendency, len(jobs)))
        
        return jobs, []
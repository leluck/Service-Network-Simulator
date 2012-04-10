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

import random
import math
import snsim.job

class JobGenerator:
    '''Defines a class that generates new jobs dependent on
    the current iteration step.
    '''
    
    def __init__(self, jobTemplates, customers, randomizer = None):
        self.jobTemplates = jobTemplates
        self.customers = customers
        
        if randomizer is None:
            self.random = random
        else:
            self.random = randomizer
        
        self.reset()
    
    def _getAmountByIteration(self, iteration):
        val = int((math.sin(iteration * 0.05) + 1.0) * 2.5)
        return val if val > 0 else 0
    
    def reset(self):
        self.nextJobId = 0
    
    def getNewJobInstances(self, iteration):
        instances = set()
        for id in xrange(0, self._getAmountByIteration(iteration)):
            randomJobTemplate = self.jobTemplates[self.random.choice([k for k in self.jobTemplates.keys()])]
            randomCustomer = self.customers[self.random.choice([k for k in self.customers.keys()])]
            instances.add(snsim.job.JobInstance(self.nextJobId, randomJobTemplate, randomCustomer))
            self.nextJobId += 1
        
        return instances
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

import snsim.resourcepool

class ServiceTemplate:
    '''Defines basic settings for a certain type of service. Based
    on this description, service instances can be spawned, that keep
    track of their status during simulation.
    Besides basic properties, a service template requires a certain
    resource pool to be assigned in order to allocate and deallocate
    required resources if a service instance based on the service
    template is spawned.
    '''
    
    def __init__(self, identifier, resources, resourcePool, ticks, revenue, penalty, maxAttempts):
        self.identifier = identifier
        
        self.resources = resources
        self.resourcePool = resourcePool
        
        self.ticks = ticks
        self.revenue = revenue
        self.penalty = penalty
        self.maxAttempts = maxAttempts
    
    def __str__(self):
        return str(self.identifier)
    
    def allocate(self, requester):
        success = dict()
        try:
            for resName, amount in self.resources.items():
                self.resourcePool.allocate(requester, resName, amount)
                success[resName] = True
        except snsim.resourcepool.ResourceCapacityExceededException as rce:
            for resName in success:
                self.resourcePool.deallocate(requester, resName, self.resources[resName])
            raise snsim.resourcepool.ResourceCapacityExceededException(str(rce))
    
    def deallocate(self, requester):
        for resName, amount in self.resources.items():    
            try:
                self.resourcePool.deallocate(requester, resName, amount)
            except snsim.resourcepool.ResourceCapacityUnderrunException:
                continue


class ServiceInstance:
    '''Defines the instantiation of a service template and adds
    runtime information.
    Service instances are the smallest (atomic)
    part of a simulation. Their dependencies are defined in
    job templates.
    '''
    
    def __init__(self, template, job):
        self.template = template
        self.ticksLeft = self.template.ticks
        self.job = job
        
        self.attempts = 0
        self.isRunning = False
        self.wasAborted = False
        self.isFinished = False
    
    def __str__(self):
        return '%s:%d:%s' % (self.job.identifier, self.job.currentTuple, self.template.identifier)
    
    def start(self):
        if self.attempts >= self.template.maxAttempts:
            raise MaxAttemptsReachedException
        if self.isRunning:
            return
        
        try:
            self.template.allocate(self)
        except snsim.resourcepool.ResourceCapacityExceededException as rce:
            self.attempts += 1
            raise snsim.resourcepool.ResourceCapacityExceededException(str(rce))
        self.isRunning = True
    
    def step(self):
        if not self.isRunning:
            return
        self.ticksLeft -= 1
        if self.ticksLeft <= 0:
            self.stop()
    
    def stop(self):
        if not self.isRunning:
            return
        try:
            self.template.deallocate(self)
            self.isRunning = False
        except snsim.resourcepool.ResourceCapacityUnderrunException:
            pass
    
    def abort(self):
        self.stop()
        self.wasAborted = True
        self.ticksLeft = 0

class MaxAttemptsReachedException(Exception):
    '''Raised when a service is requested to start but has already
    reached its maximum number of start attempts.
    '''
    pass
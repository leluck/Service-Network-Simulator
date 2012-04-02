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

import snsim.service
import snsim.resourcepool

class JobTemplate:
    '''
        Defines a possible constellation of services and holds 
        revenue and penalty due on completion of an instanced job
        based on this template.
    '''
    
    def __init__(self, identifier, scenario, signature, revenue, penalty):
        self.identifier = identifier
        self.scenario = scenario
        
        self.revenue = revenue
        self.penalty = penalty
        
        try:
            self.signature = eval(signature)
        except SyntaxError:
            raise InvalidSignatureFormatException
        
        sequence = [set(part) for part in self.signature]
        for subset in sequence:
            for element in subset:
                if len(element) != 1:
                    raise TooManyNestedScopesException(element)
                if element not in self.scenario.serviceTemplates:
                    raise InvalidServiceReferenceException(element)
    
    def __str__(self):
        return self.identifier
    
class InvalidSignatureFormatException(Exception):
    '''
        Raised when a given job signature description has and
        invalid syntax. E.g. missing brackets or quotes.
        A valid signature format is a string that defines
        tuples of service identifiers in python style.
    '''
    pass

class TooManyNestedScopesException(Exception):
    '''
        Raised when the parsed signature description is too
        deeply nested. Signatures are tuples in a tuple, that
        means they may have at most one layer of dependencies.
    '''
    pass

class InvalidServiceReferenceException(Exception):
    '''
        Raised when the parsed signature description references
        to service identifiers that are not known to the scenario
        that holds the job template.
    '''
    pass


class JobInstance:
    '''
        Defines the instantiation of a job template and adds
        certain additional properties. Furthermore, tracks the
        progress within the signature defined by the job template
        this instance is based on.
        If running a simulation, job instances deliver services
        that may be spawned respective to the signature constraints
        and based on the current progress within the signature.
    '''
    
    def __init__(self, identifier, template, customer):
        self.identifier = identifier
        self.template = template
        self.customer = customer
        
        self.serviceCount = 0
        for tuple in self.template.signature:
            self.serviceCount += len(tuple)
        
        self.reset()
    
    def __str__(self):
        return str(self.identifier)
    
    def reset(self):
        self.isFinished = False
        self.wasAborted = False
        self.currentTuple = None
        
        self.runningServices = set()
        self.pendingServices = set()
        self.finishedServices = set()
        
        self._proceed()
    
    def getPendingServices(self):
        return self.pendingServices
    
    def startService(self, service):
        if service not in self.pendingServices:
            raise ServiceNotPendingException
        try:
            service.start()
            self.runningServices.add(service)
            self.pendingServices.remove(service)
        except snsim.resourcepool.ResourceCapacityExceededException as rce:
            raise snsim.resourcepool.ResourceCapacityExceededException(str(rce))
    
    def step(self):
        if self.isFinished == True:
            return
        
        clear = set()
        for service in self.runningServices:
            service.step()
            if service.isRunning == False:
                clear.add(service)
        for service in clear:
            self.finishedServices.add(service)
            self.runningServices.remove(service)
        self._proceed() 

    def _proceed(self):
        if len(self.runningServices) != 0 or len(self.pendingServices - self.finishedServices) != 0:
            return
        
        self.currentTuple = 0 if self.currentTuple == None else self.currentTuple + 1
        self.runningServices.clear()
        self.pendingServices.clear()
        self.finishedServices.clear()
        try:
            for serviceIdentifier in self.template.signature[self.currentTuple]:
                self.pendingServices.add(snsim.service.ServiceInstance(self.template.scenario.serviceTemplates[serviceIdentifier], self))
        except IndexError:
            self.isFinished = True

    def getProgress(self):
        if self.isFinished == True:
            return 1.0
        
        finishedServiceCount = 0
        for index, tuple in enumerate(self.template.signature):
            if index < self.currentTuple:
                finishedServiceCount += len(tuple)
            if index == self.currentTuple:
                finishedServiceCount += len(self.finishedServices)
        return (float(finishedServiceCount) / float(self.serviceCount))

    def abort(self):
        self.isFinished = True
        self.wasAborted = True
        
        for service in self.runningServices:
            service.abort()

class ServiceNotPendingException(Exception):
    '''
        Raised when a service shall be started that is not part of the
        pending service set.
    '''
    pass
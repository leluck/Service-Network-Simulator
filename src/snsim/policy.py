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

class FCFSPolicy:
    '''Defines a first-come first-serve style policy.
    It will not prioritize services but rather return them
    in their naturally random order respective to the 
    job instances set.
    '''
    
    def __init__(self, parameters):
        self.name = 'FCFS Policy'
        self.parameters = parameters
    
    def __str__(self):
        return str(self.name.replace(' ', '_'))
    
    def getPrioritizedServices(self, jobInstances):
        services = []
        for job in jobInstances:
            for service in job.getPendingServices():
                services.append(service)
        services.sort(key = lambda service: '%04d%s' % (service.job.identifier, str(service.template.identifier)))
        return services


class RatioBasedPolicy:
    '''Defines a policy that aims to always accept as many
    services as possible. E.g. the accept to postpone ratio
    is maximized in each step.
    '''
    
    def __init__(self, parameters):
        self.name = 'Ratio-Based Policy'
        self.parameters = parameters
    
    def __str__(self):
        return str(self.name.replace(' ', '_'))
    
    def getPrioritizedServices(self, jobInstances):
        pending = []
        prioritized = []
        for job in jobInstances:
            for service in job.getPendingServices():
                quota = []
                for resource in service.template.resources:
                    if service.template.resourcePool.getCapacity(resource) is not None:
                        quota.append(float(service.template.resources[resource]) / float(service.template.resourcePool.getCapacity(resource)))
                priorityKey = float(sum(quota)) / float(len(quota))
                pending.append((priorityKey, service))
        for service in sorted(pending, key = lambda tuple: '%012.2f %04d %s' % (tuple[0], tuple[1].job.identifier, tuple[1]), reverse = True):
            prioritized.append(service[1])
        return prioritized


class RevenueBasedPolicy:
    '''Defines a policy that prioritizes available services by
    their expected outcome (revenue) in each simulation step. 
    It includes service-specific revenue as well as 
    job-specific revenue.
    '''
    
    def __init__(self, parameters):
        self.name = 'Revenue-Based Policy'
        self.parameters = parameters
    
    def __str__(self):
        return str(self.name.replace(' ', '_'))
    
    def getPrioritizedServices(self, jobInstances):
        pending = []
        prioritized = []
        for job in jobInstances:
            for service in job.getPendingServices():
                priorityKey = job.template.revenue + job.getProgress() * job.template.revenue
                pending.append((priorityKey, service))
        for service in sorted(pending, key = lambda tuple: '%012.2f %04d %s' % (tuple[0], tuple[1].job.identifier, tuple[1]), reverse = True):
            prioritized.append(service[1])
        return prioritized
    

class PenaltyBasedPolicy:
    '''Defines a policy that provides a prioritized selection of
    services by their expected outcome (revenue) and expected
    penalty dues.
    '''

    def __init__(self, parameters):
        self.name = 'Penalty-Based Policy'
        self.parameters = parameters
    
    def __str__(self):
        return str(self.name.replace(' ', '_'))
    
    def getPrioritizedServices(self, jobInstances):
        pending = []
        prioritized = []
        for job in jobInstances:
            for service in job.getPendingServices():
                priorityKey = job.template.revenue + job.template.penalty + job.getProgress() * job.template.revenue + job.getProgress() * job.template.penalty
                pending.append((priorityKey, service))
        for service in sorted(pending, key = lambda tuple: '%012.2f %04d %s' % (tuple[0], tuple[1].job.identifier, tuple[1]), reverse = True):
            prioritized.append(service[1])
        return prioritized


class ClassifiedPenaltyBasedPolicy:
    '''Defines a policy that provides a prioritized selection of
    services by their expected outcome (revenue) and expected
    penalty dues. Furthermore, customers are weighted by their
    respective status (gold-customer vs. non-gold customer).
    '''

    def __init__(self, parameters):
        self.name = 'Classified Penalty-Based Policy'
        self.parameters = parameters
    
    def __str__(self):
        return str(self.name.replace(' ', '_'))
    
    def getPrioritizedServices(self, jobInstances):
        pending = []
        prioritized = []
        for job in jobInstances:
            for service in job.getPendingServices():
                customerGoldStatus = 0
                if job.customer.isGold == True:
                    customerGoldStatus = 1
                priorityKey = job.template.revenue + job.template.penalty + job.getProgress() * job.template.revenue + job.getProgress() * job.template.penalty
                priorityKey *= float(self.parameters['GoldWeight']) ** customerGoldStatus
                pending.append((priorityKey, service))
        for service in sorted(pending, key = lambda tuple: '%012.2f %04d %s' % (tuple[0], tuple[1].job.identifier, tuple[1]), reverse = True):
            prioritized.append(service[1])
        return prioritized


class FailedAttemptsBasedPolicy:
    '''Defines a policy that provides a prioritized selection of
    services by their expected outcome (revenue) and expected
    penalty dues. Furthermore, it weights services by their amount
    of already failed attempts. This policy tries to avoid any
    cancellation.
    '''

    def __init__(self, parameters):
        self.name = 'Failed-Attempts-Based Policy'
        self.parameters = parameters
    
    def __str__(self):
        return str(self.name.replace(' ', '_'))
    
    def getPrioritizedServices(self, jobInstances):
        pending = []
        prioritized = []
        for job in jobInstances:
            for service in job.getPendingServices():
                priorityKey = 1.0 # Possibly set penalty-based key here as a basis for weight by failed attempts
                if service.template.maxAttempts - service.attempts > 0:
                    priorityKey *= 1.0 / float(service.template.maxAttempts - service.attempts)
                pending.append((priorityKey, service))
        for service in sorted(pending, key = lambda tuple: '%012.2f %04d %s' % (tuple[0], tuple[1].job.identifier, tuple[1]), reverse = True):
            prioritized.append(service[1])
        return prioritized

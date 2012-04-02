
class FCFSPolicy:
    '''
        Defines a first-come first-serve style policy.
        It will not prioritize services but rather return them
        in their naturally random order respective to the 
        job instances set.
    '''
    
    def __init__(self, parameters):
        self.name = 'FCFS Policy'
        self.parameters = parameters
    
    def __str__(self):
        return str(self.name)
    
    def getPrioritizedServices(self, jobInstances):
        services = []
        for job in jobInstances:
            for service in job.getPendingServices():
                services.append(service)
        services.sort(key = lambda service: '%04d%s' % (service.job.identifier, str(service.template.identifier)))
        return services


class RatioBasedPolicy:
    '''
        Defines a policy that aims to always accept as many
        services as possible. E.g. the accept to postpone ratio
        is maximized in each step.
    '''
    
    def __init__(self, parameters):
        self.name = 'Ratio-Based Policy'
        self.parameters = parameters
    
    def __str__(self):
        return str(self.name)
    
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
        for service in sorted(pending, key = lambda service: service[0]):
            prioritized.append(service[1])
        return prioritized


class RevenueBasedPolicy:
    '''
        Defines a policy that prioritizes available services by
        their expected outcome (revenue) in each simulation step. 
        It includes service-specific revenue as well as 
        job-specific revenue.
    '''
    
    def __init__(self, parameters):
        self.name = 'Revenue-Based Policy'
        self.parameters = parameters
    
    def __str__(self):
        return str(self.name)
    
    def getPrioritizedServices(self, jobInstances):
        pending = []
        prioritized = []
        for job in jobInstances:
            for service in job.getPendingServices():
                priorityKey = service.template.revenue + job.getProgress() * job.template.revenue
                pending.append((priorityKey, service))
        for service in sorted(pending, key = lambda service: service[0]):
            prioritized.append(service[1])
        return prioritized
    

class PenaltyBasedPolicy:
    '''
        Defines a policy that provides a prioritized selection of
        services by their expected outcome (revenue) and expected
        penalty dues.
    '''

    def __init__(self, parameters):
        self.name = 'Penalty-Based Policy'
        self.parameters = parameters
    
    def __str__(self):
        return str(self.name)
    
    def getPrioritizedServices(self, jobInstances):
        pending = []
        prioritized = []
        for job in jobInstances:
            for service in job.getPendingServices():
                priorityKey = service.template.revenue + job.getProgress() * job.template.revenue + service.template.penalty + job.getProgress() * job.template.penalty
                pending.append((priorityKey, service))
        for service in sorted(pending, key = lambda service: service[0], reverse = True):
            prioritized.append(service[1])
        return prioritized


class ClassifiedPenaltyBasedPolicy:
    '''
        Defines a policy that provides a prioritized selection of
        services by their expected outcome (revenue) and expected
        penalty dues. Furthermore, customers are weighted by their
        respective status (gold-customer vs. non-gold customer).
    '''

    def __init__(self, parameters):
        self.name = 'Classified Penalty-Based Policy'
        self.parameters = parameters
    
    def __str__(self):
        return str(self.name)
    
    def getPrioritizedServices(self, jobInstances):
        pending = []
        prioritized = []
        for job in jobInstances:
            for service in job.getPendingServices():
                customerGoldStatus = 0
                if job.customer.isGold == True:
                    customerGoldStatus = 1
                priorityKey = service.template.revenue + job.getProgress() * job.template.revenue + service.template.penalty + job.getProgress() * job.template.penalty
                priorityKey *= float(self.parameters['GoldWeight']) ** customerGoldStatus
                pending.append((priorityKey, service))
        for service in sorted(pending, key = lambda service: service[0], reverse = True):
            prioritized.append(service[1])
        return prioritized

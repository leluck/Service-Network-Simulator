
class ResourcePool:
    '''
        Defines a resource pool for a certain scenario.
        Services reference a certain resource pool each
        and will try to allocate resources when started and
        deallocate them when finished. A resource pool keeps
        track of available resources, current allocations and
        their respective requesters.
    '''
    
    def __init__(self, identifier, resources):
        self.identifier = identifier
        self.resources = resources
        self.requesters = []
        self.levels = dict()
        for res in self.resources:
            self.levels[res] = 0
    
    def __str__(self):
        return str(self.identifier)
    
    def getCapacity(self, identifier):
        if identifier in self.resources:
            return self.resources[identifier]
        return None
    
    def setCapacity(self, identifier, capacity):
        if identifier in self.resources and capacity >= 0:
            self.resources[identifier] = capacity
            return True
        return False
    
    def getLevel(self, identifier):
        if identifier in self.levels:
            return self.levels[identifier]
        return None
    
    def allocate(self, requester, identifier, amount):
        if identifier not in self.resources or identifier not in self.levels:
            return None
        if self.levels[identifier] + amount > self.resources[identifier]:
            raise ResourceCapacityExceededException(identifier)
        self.levels[identifier] += amount
        self.requesters.append((requester, identifier, amount))
        return True
    
    def deallocate(self, requester, identifier, amount):
        if identifier not in self.resources or identifier not in self.levels:
            return None
        if self.levels[identifier] - amount < 0:
            raise ResourceCapacityUnderrunException(identifier)
            self.levels[identifier] = 0
        else:
            self.levels[identifier] -= amount
        
        clear = set()
        for req in self.requesters:
            if req == (requester, identifier, amount):
                clear.add(req)
        for req in clear:
            self.requesters.remove(req)

class ResourceCapacityExceededException(Exception):
    '''
        Raised when a resource allocation request can not be
        satisfied.
    '''
    pass

class ResourceCapacityUnderrunException(Exception):
    '''
        Raised when a service template tries to free more resources
        than available or than it has allocated.
    '''
    pass
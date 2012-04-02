
class Customer:
    '''
        Defines a customer that is referenced by job instances
        as they are created. Holds several customer-related
        properties, such as gold status etc.
    '''
    
    def __init__(self, identifier, isGold, goldWeight):
        self.identifier = identifier
        self.isGold = isGold
        self.goldWeight = float(goldWeight)

    def __str__(self):
        return str(self.identifier)
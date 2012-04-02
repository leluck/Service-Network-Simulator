
import xml.dom.minidom

import snsim.resourcepool
import snsim.service
import snsim.job
import snsim.customer
import snsim.scenario

class XMLScenarioLoader:
    '''
        Defines a loader that parses scenarios described in XML
        format. Refer to example XML files for the exact format.
    '''
    
    def __init__(self, filename):
        self.filename = filename
        self._parse()
    
    def __str__(self):
        return 'XMLScenarioLoader (%s)' % (str(self.filename))
    
    def _parse(self):
        self.parameters = dict()
        self.resourcePools = dict()
        self.serviceTemplates = dict()
        self.jobTemplates = dict()
        self.customers = dict()
        
        root = xml.dom.minidom.parse(self.filename)
        
        parameterList = root.getElementsByTagName('Parameters')[0]
        for parameter in parameterList.childNodes:
            if parameter.nodeType == parameter.ELEMENT_NODE:
                self.parameters[parameter.nodeName] = parameter.firstChild.data
        
        poolList = root.getElementsByTagName('ResourcePools')[0]
        for pool in poolList.getElementsByTagName('ResourcePool'):
            identifier = str(pool.getElementsByTagName('Identifier')[0].firstChild.data)
            if identifier in self.resourcePools:
                print('! Skipping resource pool %s: Name already in use.' % (identifier))
                continue
            resources = dict()
            for resource in pool.getElementsByTagName('Resources')[0].childNodes:
                if resource.nodeType != resource.TEXT_NODE:
                    resources[str(resource.nodeName)] = float(resource.firstChild.data)
            self.resourcePools[identifier] = snsim.resourcepool.ResourcePool(
                identifier, 
                resources)
        
        serviceList = root.getElementsByTagName('Services')[0]
        for service in serviceList.getElementsByTagName('Service'):
            identifier = str(service.getElementsByTagName('Identifier')[0].firstChild.data)
            if identifier in self.serviceTemplates:
                print('! Skipping service template %s: Name already in use.' % (identifier))
                continue
            resourcePoolIdentifier = str(service.getElementsByTagName('ResourcePool')[0].firstChild.data)
            if resourcePoolIdentifier not in self.resourcePools:
                print('! Skipping service template %s: Given resource pool identifier \'%s\' is unknown.' % (identifier, resourcePoolIdentifier))
                continue
            resources = dict()
            for resource in service.getElementsByTagName('Resources')[0].childNodes:
                if resource.nodeType != resource.TEXT_NODE:
                    resources[str(resource.nodeName)] = float(resource.firstChild.data)
            self.serviceTemplates[identifier] = snsim.service.ServiceTemplate(
                identifier,
                resources,
                self.resourcePools[resourcePoolIdentifier],
                int(service.getElementsByTagName('Ticks')[0].firstChild.data),
                float(service.getElementsByTagName('Revenue')[0].firstChild.data),
                float(service.getElementsByTagName('Penalty')[0].firstChild.data),
                float(service.getElementsByTagName('MaxAttempts')[0].firstChild.data))
        
        jobList = root.getElementsByTagName('JobTemplates')[0]
        for job in jobList.getElementsByTagName('JobTemplate'):
            identifier = str(job.getElementsByTagName('Identifier')[0].firstChild.data)
            if identifier in self.jobTemplates:
                print('! Skipping job %s: Name already in use.' % (identifier))
                continue
            try:
                self.jobTemplates[identifier] = snsim.job.JobTemplate(
                    identifier,
                    self,
                    str(job.getElementsByTagName('Signature')[0].firstChild.data),
                    float(job.getElementsByTagName('Revenue')[0].firstChild.data),
                    float(job.getElementsByTagName('Penalty')[0].firstChild.data))
            except snsim.job.InvalidSignatureFormatException:
                print('! Skipping job %s: Signature syntax is invalid.' % (identifier))
            except snsim.job.TooManyNestedScopesException:
                print('! Skipping job %s: Too many nested scopes.' % (identifier))
            except snsim.job.InvalidServiceReferenceException as e:
                print('! Skipping job %s: Signature contains invalid service reference \'%s\'.' % (identifier, e))
    
        customerList = root.getElementsByTagName('Customers')[0]
        for customer in customerList.getElementsByTagName('Customer'):
            identifier = str(customer.getElementsByTagName('Identifier')[0].firstChild.data)
            if identifier in self.customers:
                print('! Skipping customer %s: Name already in use.' % (identifier))
                continue
            isGold = False
            if customer.getElementsByTagName('isGold')[0].firstChild.data == 'True':
                isGold = True
            goldWeight = 1
            if 'GoldWeight' in self.parameters:
                goldWeight = float(self.parameters['GoldWeight'])
            self.customers[identifier] = snsim.customer.Customer(identifier, isGold, goldWeight)
        
        print('Finished XML import. Loaded %d resource pools, %d service templates, %d job templates, %d customers.' 
              % (len(self.resourcePools), len(self.serviceTemplates), len(self.jobTemplates), len(self.customers)))
        
    def getScenario(self):
        return snsim.scenario.Scenario(self.parameters, self.resourcePools, self.serviceTemplates, self.jobTemplates, self.customers)
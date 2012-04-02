
import random

import matplotlib.pyplot as plt
import matplotlib.patches as plp

import snsim.job
import snsim.resourcepool
import snsim.service

class Scenario:
    '''
        Defines a whole scenario for the service network simulation.
        Given a set of resource pools, service templates, job templates
        and customers, a scenario is able to generate a set of job
        instances. If a policy is set, the scenario is used to run
        and control the complete simulation.
        Scenarios can be reset in order to re-run a simulation based
        on the same set of job instances with another policy set.
    '''
    
    def __init__(self, parameters, resourcePools, serviceTemplates, jobTemplates, customers):
        self.parameters = parameters
        self.resourcePools = resourcePools
        self.serviceTemplates = serviceTemplates
        self.jobTemplates = jobTemplates
        self.customers = customers
        
        self.random = random
        if 'Seed' in self.parameters:
            self.random = random.Random(self.parameters['Seed'])
        
        if 'JobCount' in self.parameters:
            self.generateJobs(int(self.parameters['JobCount']))
        else:
            self.jobInstances = set()
        
        self.policy = None
        self.reset()
    
    def __str__(self):
        jobCount = 0
        if self.jobInstances != None:
            jobCount = len(self.jobInstances)
        return 'Scenario (%dRP, %dST, %dJT, %dC || %dJI, %s)' \
            % (len(self.resourcePools), len(self.serviceTemplates), len(self.jobTemplates), len(self.customers), jobCount, self.policy)
    
    def setPolicy(self, policy):
        self.policy = policy
    
    def generateJobs(self, count):
        self.jobInstances = set()
        for id in range(0, count):
            randomJobTemplate = self.jobTemplates[self.random.choice([k for k in self.jobTemplates.keys()])]
            randomCustomer = self.customers[self.random.choice([k for k in self.customers.keys()])]
            self.jobInstances.add(snsim.job.JobInstance(id, randomJobTemplate, randomCustomer))
    
    def reset(self):
        self.numIterations = 0
        self.jobInstancesMutable = self.jobInstances.copy()
        self.plotData = dict()
        self.plotAborts = dict()
        if self.jobInstances != None:
            for job in self.jobInstances:
                job.reset()
    
    def start(self):
        self.reset()
        
        if self.policy == None or self.jobInstances == None or len(self.jobInstances) == 0:
            print('! No policy defined or no job instances generated. Not starting simulation.')
            return
        #Instantiate policy class that was set via setPolicy()
        self.policy = self.policy(self.parameters)
        
        print('Starting simulation (%s)' % (self.policy))
        iteration = 0
        while len(self.jobInstancesMutable) > 0 and iteration < 1000:
            for service in self.policy.getPrioritizedServices(self.jobInstancesMutable):
                jobIndex = '%03d' % (service.job.identifier)
                serviceIndex = '(%s,%s)' % (service.job.currentTuple, service.template.identifier)
                if jobIndex not in self.plotData:
                    self.plotData[jobIndex] = dict()
                if serviceIndex not in self.plotData[jobIndex]:
                    self.plotData[jobIndex][serviceIndex] = list()
                
                try:
                    service.job.startService(service) # Weird, but service must not start itself!
                    self.plotData[jobIndex][serviceIndex].append((iteration, service.template.ticks))
                except snsim.resourcepool.ResourceCapacityExceededException:
                    pass
                except snsim.service.MaxAttemptsReachedException:
                    service.job.abort()
                    self.plotAborts[jobIndex] = iteration
        
            clear = set()
            for job in self.jobInstancesMutable:
                job.step()
                if job.isFinished:
                    clear.add(job)
            for job in clear:
                self.jobInstancesMutable.remove(job)
            
            iteration += 1
            
        # End of main while loop
        self.numIterations = iteration
        print('Simulation finished after %d iterations.' % (self.numIterations))
    
    def report(self):
        pass
    
    def plot(self):
        fig = plt.figure(figsize = (20, 15))
        fig.subplots_adjust(top = 0.98, bottom = 0.05, left = 0.05, right = 0.98)
        plot = fig.add_subplot(1, 1, 1)
        
        vIndex = 0
        yTicks = dict()
        
        currentJob = 0
        for job in sorted(self.plotData.keys(), reverse=True):
            currentJob += 1
            
            if currentJob % 2 == 1:
                rect = plp.Rectangle((0, vIndex + 0.5), self.numIterations, len(self.plotData[job]), facecolor = 'gray', edgecolor = 'none', alpha = 0.2, fill = True)
                plt.gca().add_patch(rect)
            
            if job in self.plotAborts:
                rect = plp.Rectangle((self.plotAborts[job], vIndex + 0.5), 1, len(self.plotData[job]), facecolor = 'red', edgecolor = 'none', alpha = 1.0, fill = True)
                plt.gca().add_patch(rect)
            
            for service in sorted(self.plotData[job].keys(), reverse=True):
                vIndex += 1
                yTicks[job + ', ' + service] = vIndex
                
                jobColor = plt.get_cmap('jet')(float(currentJob)/len(self.plotData))
                plot.broken_barh(self.plotData[job][service], (vIndex - 0.25, 0.5), facecolors = jobColor)
        
        plot.set_ylim(0, vIndex + 1)
        plot.set_yticks(yTicks.values())
        plot.set_yticklabels(yTicks.keys())
        plot.grid(True)
        
        plot.set_xlim(0, self.numIterations)
        plot.set_xlabel('Time slots')
        
        fig.savefig('../figures/%s.png' % (self.policy), facecolor = fig.get_facecolor(), edgecolor = 'none')
        #plt.show()
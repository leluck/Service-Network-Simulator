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
import time

import matplotlib.pyplot as plt
import matplotlib.patches as plp

import snsim.job
import snsim.resourcepool
import snsim.service

class Scenario:
    '''Defines a whole scenario for the service network simulation.
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
        
        self.policy = None
        self.generator = None
        self.reset()
    
    def __str__(self):
        jobCount = 0
        if self.jobInstances != None:
            jobCount = len(self.jobInstances)
        return 'Scenario (%dRP, %dST, %dJT, %dC || %dJI, %s)' \
            % (len(self.resourcePools), len(self.serviceTemplates), len(self.jobTemplates), len(self.customers), jobCount, self.policy)
    
    def setPolicy(self, policy = None):
        self.policy = policy
    
    def setGenerator(self, generator = None):
        self.generator = generator
    
    def generateInitialJobs(self, count):
        self.jobInstances = set()
        for id in range(0, count):
            randomJobTemplate = self.jobTemplates[self.random.choice([k for k in self.jobTemplates.keys()])]
            randomCustomer = self.customers[self.random.choice([k for k in self.customers.keys()])]
            self.jobInstances.add(snsim.job.JobInstance(id, randomJobTemplate, randomCustomer))
    
    def reset(self):
        self.numIterations = 0
        self.loadData = list()
        self.plotData = dict()
        self.plotAborts = dict()
        
        if self.generator is None:
            self.generateInitialJobs(int(self.parameters['JobCount']))
        else:
            self.jobInstances = set()
        
        if self.jobInstances != None:
            for job in self.jobInstances:
                job.reset()
    
    def start(self, maxIterations = None):
        self.reset()
        
        if self.policy == None:
            print('! No policy defined. Not starting simulation.')
            return
        #Instantiate policy and generator
        self.policy = self.policy(self.parameters)
        self.generator = self.generator(self.jobTemplates, self.customers, randomizer = self.random)
        
        print('Starting simulation (%s)' % (self.policy))
        if maxIterations is None:
            maxIterations = 200
        iteration = 0
        abortedJobs = 0
        absoluteStartTime = time.clock()
        
        while iteration < maxIterations:
            print('Step %03d' % (iteration))
            starttime = time.clock()
            if self.generator is not None:
                self.jobInstances = self.jobInstances.union(self.jobInstances, self.generator.getJobInstances(iteration))
            
            prioritizedServiceList = self.policy.getPrioritizedServices(self.jobInstances)
            numServices = len(prioritizedServiceList)
            numJobs = len(self.jobInstances)
            for service in prioritizedServiceList:
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
                except snsim.job.ServiceNotPendingException:
                    service.job.abort()
                    self.plotAborts[jobIndex] = iteration
            
            clear = set()
            for job in self.jobInstances:
                job.step()
                if job.wasAborted:
                    abortedJobs += 1
                if job.isFinished:
                    clear.add(job)
            for job in clear:
                self.jobInstances.remove(job)
            
            elapsed = time.clock() - starttime
            print('%.4f sec for %5d active services' % (elapsed, numServices))
            
            # Collect system load information
            self.loadData.append(dict())
            self.loadData[iteration]['activeJobs'] = numJobs
            self.loadData[iteration]['activeServices'] = numServices
            self.loadData[iteration]['abortedJobs'] = abortedJobs
            self.loadData[iteration]['resources'] = dict()
            for resPool in self.resourcePools:
                self.loadData[iteration]['resources'][resPool] = dict()
                for resource in self.resourcePools[resPool].resources:
                    self.loadData[iteration]['resources'][resPool][resource] = \
                        float(self.resourcePools[resPool].levels[resource]) / float(self.resourcePools[resPool].resources[resource])
            
            iteration += 1
            
        # End of main while loop
        self.numIterations = iteration
        print('Simulation finished after %d iterations taking %.2f seconds.' % (self.numIterations, time.clock() - absoluteStartTime))
    
    def report(self, filename = None):
        if filename is None:
            filename = '../reports/%s.out' % (self.policy)
        
        with open(filename, 'w') as reportFile:
            reportFile.write('#iteration active aborted cpu memory bandwidth\n')
            it = 0
            for iteration in self.loadData:
                reportFile.write('%d %d %d %d %d %1.4f %1.4f %1.4f\n' 
                      % (it,
                         self.generator._getAmountByIteration(it),
                         iteration['activeJobs'],
                         iteration['activeServices'],
                         iteration['abortedJobs'], 
                         iteration['resources']['ResourcePool01']['CPU'], 
                         iteration['resources']['ResourcePool01']['Memory'], 
                         iteration['resources']['ResourcePool01']['Bandwidth']
                         ))
                it += 1
    
    def plot(self):
        fig = plt.figure(figsize = (int(self.generator.nextJobId / 5.0), int(self.numIterations / 5.0)))
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
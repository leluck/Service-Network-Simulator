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

import matplotlib
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
        
        self.policy = None
        self.generator = None
        self.reset()
    
    def __str__(self):
        jobCount = 0
        if self.jobInstances != None:
            jobCount = len(self.jobInstances)
        return 'Scenario (%dRP, %dST, %dJT, %dC || %dJI, %s)' \
            % (len(self.resourcePools), len(self.serviceTemplates), len(self.jobTemplates), len(self.customers), jobCount, self.policy)
    
    def setPolicy(self, policy):
        self.policy = policy(self.parameters)
    
    def setGenerator(self, generator):
        self.generator = generator(self.jobTemplates, self.customers, randomizer = self.random)
    
    def generateInitialJobs(self, count):
        self.jobInstances = set()
        for id in range(0, count):
            randomJobTemplate = self.jobTemplates[self.random.choice([k for k in self.jobTemplates.keys()])]
            randomCustomer = self.customers[self.random.choice([k for k in self.customers.keys()])]
            self.jobInstances.add(snsim.job.JobInstance(id, randomJobTemplate, randomCustomer))
    
    def reset(self):
        self.numIterations = 0
        self.sumRevenue = 0.0
        self.sumPenalty = 0.0
        self.loadData = list()
        self.plotData = dict()
        self.plotAborts = dict()
        
        self.random = random
        if 'Seed' in self.parameters:
            self.random = random.Random(self.parameters['Seed'])
        
        self.jobInstances = set()
        if self.generator is None:
            self.generateInitialJobs(int(self.parameters['JobCount']))
        else:
            self.generator.reset()
            
        for id in self.resourcePools:
            self.resourcePools[id].reset()
    
    def start(self, maxIterations = None):
        self.reset()
        
        if self.policy == None:
            print('! No policy defined. Not starting simulation.')
            return
        
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
                self.jobInstances = self.jobInstances.union(self.jobInstances, self.generator.getNewJobInstances(iteration))
            
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
                    self.sumPenalty += job.template.penalty
                if job.isFinished:
                    clear.add(job)
                if job.isFinished and not job.wasAborted:
                    self.sumRevenue += job.template.revenue
            for job in clear:
                self.jobInstances.remove(job)
            
            elapsed = time.clock() - starttime
            print('%.4f sec for %5d active services' % (elapsed, numServices))
            
            # Collect system load information
            self.loadData.append(dict())
            self.loadData[iteration]['activeJobs'] = numJobs
            self.loadData[iteration]['activeServices'] = numServices
            self.loadData[iteration]['abortedJobs'] = abortedJobs
            self.loadData[iteration]['revenue'] = self.sumRevenue
            self.loadData[iteration]['penalty'] = self.sumPenalty
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
            reportFile.write('#iteration newjobs activejobs activeservices aborted cpu memory bandwidth revenue penalty\n')
            it = 0
            for iteration in self.loadData:
                reportFile.write('%d;%d;%d;%d;%d;%1.4f;%1.4f;%1.4f;%.2f;%.2f\n' 
                      % (it,
                         self.generator._getAmountByIteration(it),
                         iteration['activeJobs'],
                         iteration['activeServices'],
                         iteration['abortedJobs'], 
                         iteration['resources']['ResourcePool01']['CPU'], 
                         iteration['resources']['ResourcePool01']['Memory'], 
                         iteration['resources']['ResourcePool01']['Bandwidth'],
                         iteration['revenue'],
                         iteration['penalty']
                         ))
                it += 1
        
        
        activeJobs = list()
        activeServices = list()
        generatedJobs = list()
        abortedJobs = list()
        resourceCPU = list()
        resourceMem = list()
        resourceBwh = list()
        sumRevenue = list()
        sumPenalty = list()
        it = 0
        for iteration in self.loadData:
            activeJobs.append(iteration['activeJobs'])
            activeServices.append(iteration['activeServices'])
            generatedJobs.append(self.generator._getAmountByIteration(it))
            abortedJobs.append(iteration['abortedJobs'])
            resourceCPU.append(iteration['resources']['ResourcePool01']['CPU'])
            resourceMem.append(iteration['resources']['ResourcePool01']['Memory'])
            resourceBwh.append(iteration['resources']['ResourcePool01']['Bandwidth'])
            sumRevenue.append(iteration['revenue'])
            sumPenalty.append(iteration['penalty'])
            it += 1
        
        fig = plt.figure(figsize = (15, 10))
        fig.patch.set_facecolor('white')
        fig.subplots_adjust(top = 0.95, bottom = 0.15, left = 0.05, right = 0.95)
        plot = fig.add_subplot(1, 1, 1, axisbg = 'w')
        plot.grid(True)
        
        plot2 = plot.twinx()
        
        font = {'family': 'serif', 'weight': 'normal', 'size': 11}
        matplotlib.rc('font', **font)
        
        l_generatedJobs = plot.plot(generatedJobs, color = '#20AB00')
        l_resourceCPU = plot2.plot(resourceCPU, color = '#708090')
        l_resourceMem = plot2.plot(resourceMem, color = '#6A5ACD')
        l_resourceBwh = plot2.plot(resourceBwh, color = '#4682B4')
        l_activeJobs = plot.plot(activeJobs, color = '#0000FF', linewidth = 3)
        l_activeServices = plot.plot(activeServices, color = '#559BEA', linewidth = 2)
        l_abortedJobs = plot.plot(abortedJobs, color = '#FF0000', linewidth = 3)
        
        plt.xlabel('Ticks')
        plt.ylabel('Amount')
        plot2.set_ylabel('Load')
        legend = fig.legend((l_activeJobs, l_activeServices, l_generatedJobs, l_abortedJobs, l_resourceCPU, l_resourceMem, l_resourceBwh), 
                            ('Active Jobs', 'Active Services', 'Generated Jobs', 'Aborted Jobs (Sum)', 'CPU Load', 'Memory Load', 'Bandwidth Load'), 
                            'lower left', ncol = 3)
        legend.get_frame().set_alpha(0.0)
        
        fig.savefig('../reports/%s_load.png' % (self.policy), facecolor = fig.get_facecolor(), edgecolor = 'none')
        #plt.show()
        
        fig = plt.figure(figsize = (15, 10))
        fig.patch.set_facecolor('white')
        fig.subplots_adjust(top = 0.95, bottom = 0.15, left = 0.05, right = 0.95)
        plot = fig.add_subplot(1, 1, 1, axisbg = 'w')
        plot.grid(True)
        
        plot2 = plot.twinx()
        
        l_activeJobs = plot.plot(activeJobs, color = '#0000FF', linewidth = 2)
        l_activeServices = plot.plot(activeServices, color = '#559BEA')
        l_abortedJobs = plot.plot(abortedJobs, color = '#FF0000', linewidth = 2)
        l_sumRevenue = plot2.plot(sumRevenue, color = '#22B300', linewidth = 3)
        l_sumPenalty = plot2.plot(sumPenalty, color = '#B30000', linewidth = 3)
        
        plt.xlabel('Ticks')
        plt.ylabel('Amount')
        plot2.set_ylabel('Load')
        legend = fig.legend((l_activeJobs, l_activeServices, l_abortedJobs, l_sumRevenue, l_sumPenalty), 
                            ('Active Jobs', 'Active Services', 'Aborted Jobs (Sum)', 'Revenue (Sum)', 'Penalty (Sum)'), 
                            'lower left', ncol = 3)
        legend.get_frame().set_alpha(0.0)
        
        fig.savefig('../reports/%s_revenue.png' % (self.policy), facecolor = fig.get_facecolor(), edgecolor = 'none')
        #plt.show()
    
    def plot(self):
        fig = plt.figure(figsize = (int(self.generator.nextJobId / 5.0), int(self.numIterations / 5.0)))
        fig.patch.set_facecolor('white')
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
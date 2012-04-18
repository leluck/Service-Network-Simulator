#!/usr/bin/python

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

#import profile

import snsim.xmlloader
import snsim.policy
import snsim.generator
import snsim.bouncer

def launch():
    loader = snsim.xmlloader.XMLScenarioLoader('../scenarios/scenario_03.xml')
    
    scenario = loader.getScenario()
    scenario.setGenerator(snsim.generator.JobGenerator)
    scenario.setBouncer(snsim.bouncer.Bouncer)
    it = 500
    
    scenario.setPolicy(snsim.policy.PenaltyBasedPolicy)
    scenario.start(maxIterations = it)
    scenario.plotLoadAndRevenue()
    scenario.bouncer.exportTrace('../reports/trace.out')
    
    #scenario.setPolicy(snsim.policy.RatioBasedPolicy)
    #scenario.start(maxIterations = it)
    #scenario.plotLoadAndRevenue()
    
    #scenario.setPolicy(snsim.policy.RevenueBasedPolicy)
    #scenario.start(maxIterations = it)
    #scenario.plotLoadAndRevenue()
    
    #scenario.setPolicy(snsim.policy.PenaltyBasedPolicy)
    #scenario.start(maxIterations = it)
    #scenario.plotLoadAndRevenue()
    
    #scenario.setPolicy(snsim.policy.ClassifiedPenaltyBasedPolicy)
    #scenario.start(maxIterations = it)
    #scenario.plotLoadAndRevenue()
    
if __name__ == '__main__':
    launch()
    #profile.run('launch()')
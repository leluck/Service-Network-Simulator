#!/usr/bin/python

import snsim.xmlloader
import snsim.policy

def launch():    
    loader = snsim.xmlloader.XMLScenarioLoader('../scenarios/scenario_01.xml')
    
    scenario = loader.getScenario()
    
    scenario.setPolicy(snsim.policy.FCFSPolicy)
    scenario.start()
    scenario.plot()
    
    scenario.setPolicy(snsim.policy.RatioBasedPolicy)
    scenario.start()
    scenario.plot()
    
    scenario.setPolicy(snsim.policy.RevenueBasedPolicy)
    scenario.start()
    scenario.plot()
    
    scenario.setPolicy(snsim.policy.PenaltyBasedPolicy)
    scenario.start()
    scenario.plot()
    
    scenario.setPolicy(snsim.policy.ClassifiedPenaltyBasedPolicy)
    scenario.start()
    scenario.plot()
    
if __name__ == '__main__':
    launch()
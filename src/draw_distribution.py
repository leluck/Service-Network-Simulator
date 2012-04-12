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


import random

def launch():
    '''Generates the complete contents of a scenario xml definition
    Distribution parameters are geared to the findings from the A*STAR
    dataset.
    '''
    
    filename = '../scenarios/generated.xml'
        
    cpuMean = 13.30
    memMean = 4600000
    seed = 'abcdefgh'
    
    rnd = random.Random(seed)
    services = []
    sBids = {}
    sPens = {}
    for i in range(ord('A'), ord('I')):
        tix = int(rnd.gauss(12, 4))
        cpu = int(rnd.gauss(cpuMean, 11.85))
        mem = int(rnd.gauss(memMean, 3700000))
        
        if tix < 0:
            tix *= -1
        if cpu < 0:
            cpu *= -1
        if mem < 0:
            mem *= -1
        
        services.append((chr(i), tix, cpu, mem))
        sBids[chr(i)] = rnd.gauss(0.95, 0.3) * float(cpu)
        sPens[chr(i)] = rnd.gauss(sBids[chr(i)], sBids[chr(i)] / 4.0)
    
    pattern = []
    numPattern = rnd.randint(4, 12)
    for i in range(0, numPattern):
        pattern.append([])
        numTuples = rnd.randint(2, 4)
        for t in range(0, numTuples):
            pattern[i].append([])
            numServices = rnd.randint(1, 4)
            for s in range(0, numServices):
                pattern[i][t].append(rnd.choice(services)[0])
    
    with open(filename, 'w') as scenarioFile:
        scenarioFile.write('''<?xml version="1.0" encoding="UTF-8"?>
<SNSimScenario>
    <Parameters>
        <Seed>%s</Seed>
        <GoldWeight>10</GoldWeight>
    </Parameters>
    <ResourcePools>
        <ResourcePool>
            <Identifier>ResourcePool01</Identifier>
            <Resources>
                <CPU>%d</CPU>
                <Memory>%d</Memory>
                <Bandwidth>1</Bandwidth>
            </Resources>
        </ResourcePool>
    </ResourcePools>
    <Customers>
        <Customer>
            <Identifier>Customer01</Identifier>
            <isGold>False</isGold>
        </Customer>
        <Customer>
            <Identifier>Customer02</Identifier>
            <isGold>False</isGold>
        </Customer>
        <Customer>
            <Identifier>Customer03</Identifier>
            <isGold>False</isGold>
        </Customer>
        <Customer>
            <Identifier>Customer04</Identifier>
            <isGold>False</isGold>
        </Customer>
        <Customer>
            <Identifier>Customer05</Identifier>
            <isGold>True</isGold>
        </Customer>
    </Customers>
    <Services>\n''' % (seed, int(cpuMean * 100), int(memMean * 100)))
    
        for s in services:
            scenarioFile.write('''        <Service>
            <Identifier>%s</Identifier>
            <ResourcePool>ResourcePool01</ResourcePool>
            <Ticks>%d</Ticks>
            <Resources>
                <CPU>%d</CPU>
                <Memory>%d</Memory>
                <Bandwidth>0</Bandwidth>
            </Resources>
            <MaxAttempts>100</MaxAttempts>
        </Service>\n''' % (s[0], s[1], s[2], s[3]))
        
        scenarioFile.write('''    </Services>
    <JobTemplates>\n''')
    
        i = 1
        for p in pattern:
            rev = 0.0
            pen = 0.0
            for t in p:
                for s in t:
                    rev += sBids[s]
                    pen += sPens[s]
            
            scenarioFile.write('''        <JobTemplate>
            <Identifier>Pattern%02d</Identifier>
            <Signature>%s</Signature>
            <Revenue>%.2f</Revenue>
            <Penalty>%.2f</Penalty>
        </JobTemplate>\n''' % (i, str(p).replace('[', '(').replace(']', ')'), rev, pen))
            i += 1
    
        scenarioFile.write('''    </JobTemplates>
</SNSimScenario>''')
    
if __name__ == '__main__':
    launch()
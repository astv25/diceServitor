# %%
import math
import random
import logging as log
import re #([\d]+)d([\d]+)([><d+-/*]?[=l]?)([\d]+)?([+-/*\d]+)?(#.+)?

# %%
#Test cases:
a = "1D100"
b = "1d100>50"
c = "1d100<=50"
d = "10d100"
e = "1d10+5"
f = "3d10dl2"
g = "3d10dl2+5-3#comment"
h = "1d10+2-4"
i = "hkhkjhkh"
j = "1d10#Hello world"
k = "5d10sd"
l = "5d10+5sa"

# %%
testCases = [a,b,c,d,e,f,g,h,i,j,k,l]

logFile = 'output.log'
logLevel = log.INFO
log.basicConfig(filename=logFile,level=logLevel)

# %%
def diceRolling(input):
    try:
        log.info("Rolling: " +input)
        input = input.lower().strip() #basic formatting
        pattern_d = re.compile('([\d]+)d([\d]+)([><d]?[=l]?)([\d]+)?([+-/*\d]+)?(#.+)?')
        matches = pattern_d.split(input)
        matches = list(filter(None,matches))
        #sort ascending, sort descending, or don't sort at all
        #using pop to avoid altering the rest of the code
        sortatall=False
        sortdescending=False
        if matches[-1] == 'sd':
            sortatall=True
            sortdescending=True
            matches.pop()
        if matches[-1] == 'sa':
            sortatall=True
            matches.pop()

        test = (len(matches))
        rolls = []
        mathSymbols = ['+','-','/','*']
        modSymbols = ['>','<','d']

        # for match in matches:
            # print(match)

        def rolling(numDice,numSides,sortAtAll,sortDescending):
            for i in range(1,numDice+1):
                random.seed()
                roll = random.randrange(1,numSides+1)
                rolls.append(roll)
            if sortAtAll:
                rolls.sort(reverse=sortDescending)
            return rolls

        def compareOrDrop(rolls,mod,num):
            #mod:  > < d >= <=
            #rolls:  list of rolls
            #num:  TN or drop count
            origrolls = []
            compequal=False
            compswitch=False
            dropped = []
            total = 0
            out = []
            origrolls.extend(rolls)
            validops = ['>', '>=', '<=', '<', 'dl']
            if not mod in validops:
                return "Compare/Drop:  Invalid operator"
            #drop lowest X
            if mod == 'dl':
                print("Rolled: " + str(origrolls))
                index=1
                tmprolls=[]
                tmprolls.extend(rolls)
                tmprolls.sort()
                while index <= num:
                    dropped.append(tmprolls[0])
                    tmprolls.pop(0)
                    index+=1
                return tmprolls
            #roll over/at/under TN
            if '>' in mod:
                compswitch=True
            if '=' in mod:
                compequal=True
            index=0
            while index<len(rolls):
                passfail=False
                if(compswitch):
                    degrees = rolls[index] - num
                else:
                    degrees = num - rolls[index]
                degrees = degrees / 10
                if(compequal):
                    if(degrees>=0):
                        passfail=True
                else:
                    if(degrees>0):
                        passfail=True
                out.append("Rolled {0}, TN {1}.  {2} Degrees of {3}!".format(rolls[index], num, degrees, "Success" if (passfail) else "Failure"))
                index+=1
            return out


        def mathHandling(input, total):
            #total = 0
            nums = input
            for x in mathSymbols:
                nums = nums.replace(x," ")
            nums = nums.split()
            #print(input)
            #print(nums)
            for x in input:
                if x in mathSymbols:
                    if x == '*':
                        total *= int(nums[0])
                        nums.pop(0)
                    if x == '/':
                        total /= int(nums[0])
                        nums.pop(0)
                    if x == '+':
                        total += int(nums[0])
                        nums.pop(0)
                    if x == '-':
                        total -= int(nums[0])
                        nums.pop(0)
            return total


        def two():
            return rolling(int(matches[0]),int(matches[1]),sortatall,sortdescending)
        def three():
            results = rolling(int(matches[0]),int(matches[1]),sortatall,sortdescending)

            if('#' in matches[2]):
                return str(results) +" "+ matches[2]
            if(matches[2][0] in mathSymbols):
                resultsTotal = 0
                for x in results:
                    resultsTotal += x
                #resultsTotal += mathHandling(matches[2])
                resultsTotal = mathHandling(matches[2],resultsTotal)
                return str(results) + " Total = " + str(resultsTotal)

            return "Are you sure?"
        def four():
            results = rolling(int(matches[0]),int(matches[1]),sortatall,sortdescending)
            dropTotal = 0
            droppedOutput = str(results)
            if (matches[2][0] in modSymbols):
                mod = matches[2]
            if (matches[2][0] in mathSymbols):
                resultsTotal = 0
                for x in results:
                    resultsTotal += x
                #resultsTotal += mathHandling(matches[2])
                resultsTotal = mathHandling(matches[2], resultsTotal)
                return str(results) + " Total = " + str(resultsTotal) +" "+ matches[3]
            if (matches[3].isdigit()):
                modNum = matches[3]
                modNum = int(modNum)
            else:
                return "Reconsider this entry... and your life choices"
            output = compareOrDrop(results,mod,modNum)
            if(matches[2][0] == 'd'):
                for x in output:
                    dropTotal += int(x)
                return "Original rolls = "+ str(droppedOutput) +" After Dropping = " + str(output) + " Total = " + str(dropTotal)
            return output
        def five():
            results = rolling(int(matches[0]),int(matches[1]),sortatall,sortdescending)
            droppedOutput = str(results)
            if (matches[2][0] in modSymbols and matches[3][0].isdigit()):
                mod = matches[2]
                modNum = int(matches[3])
            else:
                return "Something ain't right chief"
            if('#' in matches[4]):
                output = compareOrDrop(results,mod,modNum)
                if matches[2][0] == 'd':
                    resultsTotal = 0
                    for x in output:
                        resultsTotal += x
                    return "Original rolls = "+ str(droppedOutput) +" After Dropping = " + str(output) +" Total = "+ str(resultsTotal) +str(matches[4])
                return str(output) + " " + str(matches[4])
            if (matches[4][0] in mathSymbols):
                output = compareOrDrop(results,mod,modNum)
                if matches[2][0] == 'd':
                    resultsTotal = 0
                    for x in output:
                        resultsTotal += x
                    #resultsTotal += mathHandling(matches[4])
                    resultsTotal = mathHandling(matches[4],resultsTotal)
                    return "Original rolls = "+ str(droppedOutput) +" After Dropping = " + str(output) + " Total = " + str(resultsTotal)
                else:
                    resultsTotal = 0
                    for x in results:
                        resultsTotal += x
                    #resultsTotal += mathHandling(matches[4])
                    resultsTotal = mathHandling(matches[4],resultsTotal)
                    return str(output) + " Total = " + str(resultsTotal)

            return "Literally How?"
        def six():
            results = rolling(int(matches[0]),int(matches[1]),sortatall,sortdescending)
            mod = matches[2]
            modNum = int(matches[3])
            droppedOutput = str(results)
            output = compareOrDrop(results,mod,modNum)
            if matches[2][0] == 'd':
                resultsTotal = 0
                for x in output:
                    resultsTotal += x
                #resultsTotal += mathHandling(matches[4])
                resultsTotal = mathHandling(matches[4],resultsTotal)
            else:
                droppedOutput == None
                resultsTotal = 0
                for x in results:
                    resultsTotal += x
                #resultsTotal += mathHandling(matches[4])
                resultsTotal = mathHandling(matches[4],resultsTotal)
            if droppedOutput == None:
                return str(output) + " Total = " + str(resultsTotal) +" "+ matches[5]
            else:
                return "Original rolls = "+ str(droppedOutput) +" After Dropping = " + str(output) + " Total = " + str(resultsTotal) +" "+ matches[5]


        def groupCases(argument):
            switcher = {
                2:two,
                3:three,
                4:four,
                5:five,
                6:six
            }

            func = switcher.get(argument, lambda: "Invalid Length")
            return (func())

        return groupCases(test)

    except Exception as e:
        log.error(str(e))



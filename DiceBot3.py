import math
import random
import re #([\d]+)d([\d]+)([><d+-/*]?[=l]?)([\d]+)?([+-/*\d]+)?(#.+)?


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
testCases =[a,b,c,d,e,f,g,h,i,j]

def diceRolling(input):
    try:
        print("Rolling: " +input)
        random.seed()
        input = input.lower().strip() #basic formatting
        pattern_d = re.compile('([\d]+)d([\d]+)([><d]?[=l]?)([\d]+)?([+-/*\d]+)?(#.+)?') 
        matches = pattern_d.split(input)
        matches = list(filter(None,matches))
        test =(len(matches))
        rolls = []
        mathSymbols = ['+','-','/','*']
        modSymbols = ['>','<','d']
        # for match in matches:
        #     print(match)
        def rolling(numDice,numSides):
            for i in range(1,numDice+1):
                roll = random.randrange(1,numSides+1)
                rolls.append(roll)
            rolls.sort()
            return rolls

        def compareOrDrop(rolls,mod,num):
            #mod:  > < d >= <=
            #rolls:  list of rolls
            #num:  TN or drop count
            origrolls = []
            compequal=False            
            dropped = []
            total = 0
            out = []
            origrolls.extend(rolls)
            validops = ['>', '>=', '<=', '<', 'dl']
            if not mod in validops:
                return "Compare/Drop:  Invalid operator"
            #drop lowest X
            if mod == 'dl':    
                index=1
                while index <= num:
                    dropped.append(rolls[0])
                    rolls.pop(0)
                    index+=1
                #total=sum(rolls)
                #out.append("Rolled {0}.  Dropped {1}.  Total {2}".format(origrolls,dropped,total))
                #print(out)
                return rolls
            if mod == '>' or mod == '>=':
                if '=' in mod:
                    compequal=True
                index=0
                while index<len(rolls):
                    passfail=False
                    degrees = rolls[index] - num
                    degrees = degrees / 10
                    if(compequal):
                        if(degrees>=0):
                            passfail=True
                    else:
                        if(degrees>0):
                            passfail=True
                    out.append("Rolled {0}, TN {1}.  {2} Degrees of {3}!\n".format(rolls[index], num, degrees, "Success" if (passfail) else "Failure"))
                    index+=1
                #print(out)
                return out
            if mod == '<' or mod == '<=':
                if '=' in mod:
                    compequal=True
                index=0
                while index<len(rolls):
                    passfail=False
                    degrees = num - rolls[index]
                    degrees = degrees / 10
                    if(compequal):
                        if(degrees>=0):
                            passfail=True
                    else:
                        if(degrees>0):
                            passfail=True
                    out.append("Rolled {0}, TN {1}.  {2} Degrees of {3}!\n".format(rolls[index], num, degrees, "Success" if (passfail) else "Failure"))
                    index+=1
                #print(out)
                return out
                    

        def mathHandling(input):
            total = 0
            nums = input
            for x in mathSymbols:
                nums = nums.replace(x," ")
            nums = nums.split()
            for x in input:
                if x in mathSymbols:
                    if x == '+':
                        total += int(nums[0])
                        nums.pop(0)
                    if x == '-':
                        total -= int(nums[0])
                        nums.pop(0)
                    if x == '/':
                        total /= int(nums[0])
                        nums.pop(0)
                    if x == '*':
                        total *= int(nums[0])
                        nums.pop(0)
            return total           


        def two():
            return rolling(int(matches[0]),int(matches[1]))
        def three():
            results = rolling(int(matches[0]),int(matches[1]))
            
            if('#' in matches[2]):
                return str(results) + matches[2]
            if(matches[2][0] in mathSymbols):
                resultsTotal = 0
                for x in results:
                    resultsTotal += x
                resultsTotal += mathHandling(matches[2])
                return str(results) + " Total: " + str(resultsTotal)
                
            return "Are you sure?"
        def four():
            results = rolling(int(matches[0]),int(matches[1]))
            dropTotal = 0
            if (matches[2][0] in modSymbols):
                mod = matches[2]                
            if (matches[2][0] in mathSymbols):
                resultsTotal = 0
                for x in results:
                    resultsTotal += x
                resultsTotal += mathHandling(matches[2])
                return str(results) + " Total: " + str(resultsTotal) +" "+ matches[3]
            if (matches[3].isdigit()):
                modNum = matches[3]
                modNum = int(modNum)
            else:
                return "Reconsider this entry... and your life choices"
            results = compareOrDrop(results,mod,modNum)
            if(matches[2][0] == 'd'):
                for x in results:
                    dropTotal += int(x)
                return str(results) + " Total: " + str(dropTotal)
            return results    
        def five():
            results = rolling(int(matches[0]),int(matches[1]))
            if (matches[2][0] in modSymbols and matches[3][0].isdigit()):
                mod = matches[2]
                modNum = int(matches[3])
            else:
                return "Something ain't right chief"
            if('#' in matches[4]):
                output = compareOrDrop(results,mod,modNum)
                return str(output) + matches[4]
            if (matches[4][0] in mathSymbols):
                output = compareOrDrop(results,mod,modNum)
                if matches[2][0] == 'd':
                    resultsTotal = 0
                    for x in output:
                        resultsTotal += x
                    resultsTotal += mathHandling(matches[4])
                else:
                    resultsTotal = 0
                    for x in results:
                        resultsTotal += x
                    resultsTotal += mathHandling(matches[4])   

                return str(output) + "Total = " + str(resultsTotal)

            return "Literally How?"
        def six():
            results = rolling(int(matches[0]),int(matches[1]))
            mod = matches[2]
            modNum = int(matches[3])
            output = compareOrDrop(results,mod,modNum)
            if matches[2][0] == 'd': 
                resultsTotal = 0
                for x in output:
                    resultsTotal += x
                resultsTotal += mathHandling(matches[4])
            else:
                resultsTotal = 0
                for x in results:
                    resultsTotal += x
                resultsTotal += mathHandling(matches[4])
            return str(output) + "Total = " + str(resultsTotal) +" "+ matches[5]

        def groupCases(argument):
            switcher = {
                2:two,
                3:three,
                4:four,
                5:five,
                6:six
            }

            func = switcher.get(argument, lambda: "Invalid Length")
            print(func())
        
        groupCases(test)
    except Exception as e:
        print(str(e))
    

#diceRolling("3d10dl2+5+6#I am the comment")
# diceRolling("1d100<=30")
#diceRolling("3d10dl1")
# diceRolling("1d100>45")
#diceRolling("2d100<30")
for test in testCases:
    diceRolling(test)
    print("End Roll")


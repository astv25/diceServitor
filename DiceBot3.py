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
            return rolls

        def compareOrDrop(rolls,mod,num):
            

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
            if (matches[2][0] in modSymbols):
                mod = matches[2]
            else:
                return "Bad stop it"   
            if (matches[3].isdigit()):
                modNum = matches[3]
            else:
                return "Reconsider this entry... and your life choices"    

            


            return "this is a roll with a single mod"
        def five():
            return "this is a die roll with multiple mods and/or a comment"
        def six():
            return "This is a die roll with multiple mods and a comment"

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
    

diceRolling("1d2>=4")

# for test in testCases:
#     diceRolling(test)
#     print("End Roll")


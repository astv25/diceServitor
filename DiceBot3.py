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
j = "1d2"
testCases =[a,b,c,d,e,f,g,h,i,j]

def diceRolling(input):
    try:
        input = input.lower().strip() #basic formatting
        pattern_d = re.compile('([\d]+)d([\d]+)([><d+-/*]?[=l]?)([\d]+)?([+-/*\d]+)?(#.+)?') 
        matches = pattern_d.split(input)
        matches = list(filter(None,matches))
        test =(len(matches))
        # for match in matches:
        #     print(match)

        def two():
            return "this is a normal die roll"
        def three():
            return "A normal die roll with comment"
        def four():
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
    

diceRolling(b)

# for test in testCases:
#     diceRolling(test)
#     print("End Roll")


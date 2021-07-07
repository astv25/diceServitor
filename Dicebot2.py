import random

a = "1D100"
b = "1d100tn50"
c = "1d100tn+50"
d = "10d100"
e = "1d10+5"
f = "3d10dl2"
g = "3d10dl2+5"
h = "1d10+2-4"
i = "hkhkjhkh"
j = "1d2"
testCases =[a,b,c,d,e,f,g,h,i]



def diceRolling(input):
    random.seed()
    mathNum = 0
    numSides = ""
    compareNum = ""
    comparator = ""    
    output = ""
    rolls = []
    input = input.lower().strip() #basic formatting
    try:
        index = int(input.index('d')) #Finds the first 'd' in the string which is our indicator for number of dice to the left
        numDice = int(input[:index])  #Takes the start of the string to but not including 'd' 
        index+=1 #We want to start evaluating to the right of 'd'
        while index < len(input):
            if input[index].isdigit(): #We are now interested in finding the sides of the dice to be rolled. 
                numSides += input[index] #We concatenate the digits and will later cast numSides to int
                index+=1
            else:                
                break
            

        i = 0
        print("Rolling: " +input)
        while i < int(numDice):
            roll = random.randrange(1,int(numSides)+1)
            rolls.append(roll)
            i+=1
        print("Rolled:  {0}".format(rolls))
        if input[index]=='>' and input[index+1].isdigit():
            comparator = input[index]
            index+=1            
            compareNum = buildCompareNum(index,input)
        if input[index]=='>' and input[index+1]=='=':
            comparator += input[index]
            comparator += input[index+1]
            index+=2            
            compareNum = buildCompareNum(index,input)
        if input[index]=='<' and input[index+1].isdigit():
            comparator = input[index]
            index+=1            
            compareNum = buildCompareNum(index,input)
        if input[index]=='<' and input[index+1]=='=':
            comparator += input[index]
            comparator += input[index+1]
            index+=2            
            compareNum = buildCompareNum(index,input)        
        rolls.sort()
        compareNum=int(compareNum)
        for roll in rolls:
            passfail=False
            tmp = roll            
            hellisemptyandthedemonsarehere = str(roll) + comparator + str(compareNum)
            if(eval(hellisemptyandthedemonsarehere)):
                #My regrets are numerous
                passfail=True
            tmp = tmp - compareNum
            tmp = tmp / 10
            tmp = abs(tmp)
            print("Rolled:  {0}, Target: {1}; {2} Degrees of {3}".format(roll, compareNum, tmp, "Success" if(passfail) else "Failure"))

        print(rolls)

    except Exception as e:
        print(str(e))

def buildCompareNum(index,input):
    out = ""
    while index < len(input):
        if input[index].isdigit():
            out+=input[index]
        index+=1
    return out

#diceRolling("1d100>30")
#diceRolling("1d100>=30")
#diceRolling("1d100<30")
#diceRolling("1d100<=30")
diceRolling("3d100<=55")
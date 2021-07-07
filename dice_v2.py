import random

def dice(numdie:int, dxx:int, mod=0, tn=False, tearing=False, tnhilo=False):
    #Usage:
    #dice(3,10) will roll 3d10 and report the total
    #dice(2,10,9) will roll 2d10, add 9, and report the total
    #dice(1,100,35,True) will roll 1d100 with TN <=35 and report degrees of success or failure
    #dice(1,100,35,True,False,True) will roll 1d100 with TN >=35
    #dice(3,10,0,False,True) will roll 3d10, drop the lowest X die specified by mod, and report the total.
    #there is no handling for rolling a Target Number and Tearing
    #returns a string with the results of dice rolls; print statements go to the console for debugging
    random.seed() #(Re)Initialize RNG each time
    passfail = False
    #Invalid argument handling
    if(numdie==0 or dxx==0):
        out = "Invalid dice combination: {0}d{1}".format(numdie,dxx)
        print(out)
        return out
    if(tn and tearing):
        out = "Unable to handle Target Number and Tearing at the same time!"
        print(out)
        return out
    #Handling for Tearing (drop X lowest)
    if(tearing):
        index=1
        rolls=[]
        origrolls=[]
        dropped=[]
        while index<=numdie:
            roll = random.randint(1,dxx)
            rolls.append(roll)
            index+=1
        #lowest = min(rolls)
        #total = sum(rolls)-lowest
        print("Raw rolls: {}".format(rolls))
        rolls.sort()
        origrolls.extend(rolls)
        print("Sorted rolls: {}".format(rolls))
        index=1
        while index<=mod:
            dropped.append(rolls[0])
            rolls.pop(0)
            index+=1
        total=sum(rolls)
        out = "Rolled {0}.  Dropped {1}.  Total {2}".format(origrolls,dropped,total)
        print(out)
        return out
    #Handling for Target Number
    if(tn):        
        index=1
        out = []
        while index<=numdie:
            passfail = False
            roll = random.randint(1,dxx)
            if(tnhilo):                
                degrees = roll - mod
                degrees = degrees / 10
                if(degrees>=0):
                    passfail=True
                degrees = abs(degrees)
            else:
                degrees = mod - roll
                degrees = degrees / 10
                if(degrees>=0):
                    passfail=True
                degrees = abs(degrees)
            print("Rolled: ", roll)
            print("TN    : ", mod)
            out.append("Rolled {0}, TN {1}. {2} Degrees of {3}!".format(roll, mod, degrees, "Success" if(passfail) else "Failure"))
            index+=1
        print(out)
        return out
    #Handling for modified roll
    if(tn == False and mod!=0):
        index=1
        rolls=[]
        total=0
        while index<=numdie:
            roll = random.randint(1,dxx)
            rolls.append(roll)
            total+=roll
            index+=1
        total+=mod
        out = "Rolled {0} {1} {2}. Total {3}".format(rolls, "+" if(mod>0) else "-", abs(mod), total)
        print(out)
        return out
    #Handling for plain roll
    if(tn== False and mod==0):
        index=1
        rolls=[]
        total=0
        while index<=numdie:
            roll=random.randint(1,dxx)
            rolls.append(roll)
            total+=roll
            index+=1
        out = "Rolled {0}.  Total {1}".format(rolls,total)
        print(out)
        return out

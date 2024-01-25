import csv

import collections

import openpyxl

from copy import deepcopy

import random

import subprocess

# List of all enchantments
enchantments = [
    'Aqua Affinity (I)',
    'Bane of Arthropods (V)',
    'Blast Protection (IV)',
    'Channeling (I)',
    'Curse of Binding (I)',
    'Curse of Vanishing (I)',
    'Depth Strider (III)',
    'Efficiency (V)',
    'Feather Falling (IV)',
    'Fire Aspect (II)',
    'Fire Protection (IV)',
    'Flame (I)',
    'Fortune (III)',
    'Frost Walker (II)',
    'Impaling (V)',
    'Infinity (I)',
    'Knockback (II)',
    'Looting (III)',
    'Loyalty (III)',
    'Luck of the Sea (III)',
    'Lure (III)',
    'Mending (I)',
    'Multishot (I)',
    'Piercing (IV)',
    'Power (V)',
    'Projectile Protection (IV)',
    'Protection (IV)',
    'Punch (II)',
    'Quick Charge (III)',
    'Respiration (III)',
    'Riptide (III)',
    'Sharpness (V)',
    'Silk Touch (I)',
    'Smite (V)',
    'Thorns (III)',
    'Sweeping Edge (III)',
    'Unbreaking (III)'
]


def GetTradersCSV(enchantmentsLst, file):

    with open(file, newline='') as csvfile:
        lst = list(csv.reader(csvfile))

    traderList = {}

    for i in range(len(lst)):
        for j in range(len(lst[0])):
            # skip empty cells and cells containing trash
            if (lst[i][j] not in enchantmentsLst):
                continue

            # if this is the first entry for a trader, create a new dictionary
            if ((i) % 4 == 0):
                trades = [lst[i][j]]
                traderList[(i // 4,j)] = trades
                continue

            # If this is not the first entry, add it to the right entry.
            traderList[(i // 4,j)].append(lst[i][j])
            
    return traderList

class Sheet:

    # constructor function    
    def __init__(self, file = ""):
        self.wrkbk = openpyxl.load_workbook(file)
        self.sh = self.wrkbk.active

    # Define getter 
    def __getitem__(self, index):
        i, j = index
        # +2 as we 0 index in the code below but openpyxl 1 indexes, also data is shifted down and right by 1
        cell_obj = self.sh.cell(row=i+2, column=j+2)
        return cell_obj.value


def GetTradersXLSX(enchantmentsLst, file):

    sheet = Sheet(file)

    traderList = {}

    for i in range(32):
        for j in range(9):
            # skip empty cells and cells containing trash
            if (sheet[i,j] not in enchantmentsLst):
                continue

            # if this is the first entry for a trader, create a new dictionary
            if ((i) % 4 == 0):
                trades = [sheet[i,j]]
                traderList[(i // 4,j)] = trades
                continue

            # If this is not the first entry, add it to the right entry.
            traderList[(i // 4,j)].append(sheet[i,j])

    return traderList


def GreedySetCover(enchantments,inputDict,force,randomize):
    if (randomize):
        randomDict = list(inputDict.items())
        random.shuffle(randomDict)
        inputDict = dict(randomDict)

    #Should sort by number of values in decreasing order to increase chances of including the ones with many enchantments
    traderDict = dict(sorted(inputDict.items(), key=lambda x: len(x[1]), reverse=True)) 

    covered = set()
    selectedTraders = []

    # Force keep double enchantments
    if (force):
        for index in traderDict:
            # if (traderDict[index][0] == "Mending (I)" and traderDict[index][1] == "Mending (I)"):
            if len(set(traderDict[index])) != len(traderDict[index]):
                selectedTraders.append(index)
                covered |= set(traderDict[index])


    while len(covered) < len(enchantments):
        best_index = None
        best_count = 0
        for index in traderDict:

            if index in selectedTraders:
                continue

            current_set = set(traderDict[index])
            count = len([e for e in enchantments if e not in covered and e in current_set])
            # if count > best_count and len(current_set) > 2: #only consider sets larger than 2
            if count > best_count: 

                best_count = count
                best_index = index
        if best_index is None:
            break
        selectedTraders.append(best_index)
        covered |= set(traderDict[best_index])

    #Print missing trades
    if len(covered) < len(enchantments):
        print("Missing trades:")
        for e in enchantments:
            if e not in covered:
                print(e)
    

    return selectedTraders


def N3GreedySetCover(enchantments,inputDict):


    smallestSetSize = float("inf")

    bestSet = []

    covered = set()

    # A loop running n times brings the asymptotic running time up to n^3, which is still better than 2^n.
    for i in range(len(inputDict)):

        covered = set()

        selectedTraders = []

        #Shuffle for getting better output
        randomDict = list(inputDict.items())
        random.shuffle(randomDict)
        inputDict = dict(randomDict)

        # Sort by number of values in decreasing order to increase chances of including the ones with many enchantments
        # This should not change the shuflleness between same-length entries
        traderDict = dict(sorted(inputDict.items(), key=lambda x: len(x[1]), reverse=True)) 

        while len(covered) < len(enchantments):
            best_index = None
            best_count = 0
            for index in traderDict:

                if index in selectedTraders:
                    continue

                current_set = set(traderDict[index])
                count = len([e for e in enchantments if e not in covered and e in current_set])
                # if count > best_count and len(current_set) > 2: #only consider sets larger than 2
                if count > best_count: 

                    best_count = count
                    best_index = index
            if best_index is None:
                break
            selectedTraders.append(best_index)
            covered |= set(traderDict[best_index])

        if (len(selectedTraders) < smallestSetSize):
            smallestSetSize = len(selectedTraders)
            bestSet = selectedTraders            

    # Print missing trades
    if len(covered) < len(enchantments):
        print("Missing trades:")
        for e in enchantments:
            if e not in covered:
                print(e)

    return bestSet    


def GodMachine(traderDict,selectedTraders,printKillDict,printKeepDict):
    print(f"\nOut of {len(traderDict)} villagers {len(selectedTraders)} is enough to cover all enchantments.")

    # Split traders into keep and kill
    killDict = deepcopy(traderDict)
    keepDict = {}
    for index in selectedTraders:
        keepDict[index] = traderDict[index]
        killDict.pop(index, None)

    # How many trades and how many per villager?
    numTrades = 0
    for trader in keepDict:
        for trade in keepDict[trader]:
            numTrades += 1
    print(f"Totaling {numTrades} trades, averaging {numTrades/len(keepDict):.2f} trades per villager.")

    # We need to know how many high demand enchantments we have (should be >1)
    print("\nThis is the number of high demand enchantments:")
    print('\n'.join(f"{e}: {sum(v.count(e) for v in keepDict.values())}" for e in ['Mending (I)', 'Unbreaking (III)', 'Efficiency (V)']))
    # These three lines do the same thing as the line above, but is much easier to read
    # print(f"Mending: {sum(value.count('Mending (I)') for value in keepDict.values())}")
    # print(f"Unbreaking: {sum(value.count('Unbreaking (III)') for value in keepDict.values())}")
    # print(f"Efficiency: {sum(value.count('Efficiency (V)') for value in keepDict.values())}")


    # Sort and print kill list
    if (printKillDict):
        print(f"\nKill these {len(killDict)} villagers:")
        killDict = collections.OrderedDict(sorted(killDict.items()))
        for index in killDict: 
            print(f"{index},{killDict[index]}")

    # Sort and print keep list
    if (printKeepDict):
        print(f"\nKeep these {len(keepDict)} villagers:")
        keepDict = collections.OrderedDict(sorted(keepDict.items()))
        for index in keepDict: 
            print(f"{index},{keepDict[index]}")    

    return killDict, keepDict


def Avoid(enchantments, traderDict):
    print("\nTo get better villagers avoid:")

    perfectTrades = ["Mending (I)"]

    for trader in traderDict:
        if (len(traderDict[trader]) == 4):
            for trade in traderDict[trader]:
                if (trade not in perfectTrades):
                     perfectTrades.append(trade)

    perfectTrades.sort()

    for trade in perfectTrades:
        count = 0

        for trader in traderDict:
            count += traderDict[trader].count(trade)


        print(f"{count} x {trade}")





def LookFor(enchantments, traderDict):
    print("\nTo get better villagers look for:")

    # We want to find any trades that don't occour in perfect traders (4 trades). This could also be done by 
    # first iterating through perfect traders and adding their trades to a list, and then iterate through not 
    # pefect traders and retain any trades not in that list. 
    # instead we simply sort the dict by number of trades, as we then know that perfect traders get handled first.
    traderDict = dict(sorted(traderDict.items(), key=lambda x: len(x[1]), reverse=True)) 

    perfectTrades = []

    wantedTrades = ["Unbreaking (III)","Efficiency (V)", "Mending (I)"] #High demand trades

    for trader in traderDict:
        for trade in traderDict[trader]:
            if (len(traderDict[trader]) >= 4):
                if (trade not in perfectTrades):
                     perfectTrades.append(trade)
            else:
                if (trade not in wantedTrades and trade not in perfectTrades and "(I)" not in trade):
                    wantedTrades.append(trade)

    wantedTrades.sort()

    for trade in wantedTrades:
        print(trade)


def CountEnchantments(enchantments, traderDict):
    print("\nThe enchantments are covered in this way:")
    globalCount = 0
    for enchantment in enchantments:
        count = 0
        for trader in traderDict:
            count += traderDict[trader].count(enchantment)
            globalCount += traderDict[trader].count(enchantment)
        print(f"{count} x {enchantment}")
    print(f"Totaling {globalCount} enchamntents or {globalCount/len(traderDict):.2f} across {len(traderDict)} traders")


test = "clear"
subprocess.run(test, shell=True, capture_output=False)


print("------------------ A-team ------------------")

traderDict = GetTradersXLSX(enchantments,"enchantments.xlsx")

# selectedTraders = GreedySetCover(enchantments, traderDict, False, False)

selectedTraders = N3GreedySetCover(enchantments, traderDict)

killDict, keepDict = GodMachine(traderDict,selectedTraders, False, True)

LookFor(enchantments, keepDict)

#Avoid(enchantments, keepDict)


CountEnchantments(enchantments,keepDict)

# print("\n\n------------------ B-team ------------------")

# selectedTraders = GreedySetCover(enchantments, killDict, False, False)

# kill, keep = GodMachine(killDict,selectedTraders, False, True)

# CountEnchantments(enchantments,keep)


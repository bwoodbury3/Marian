import random
import math
import time

def pigEngine(outputFunction, inputFunction):   
    outputFunction ("Let's play Pig!\n--------\nHere's how to play.\nWe will take turns rolling the dice.\nYou can continue to roll as many times as you want before you end your turn.\n\
The numbers that you roll will be added to your point total for that turn.\nAt the end of your turn, that score will be added to your overall point total.\nYou may end your turn whenever you want, but be careful!\
\nRolling a 1 will reset your turn's point total to 0 and you will have to pass your turn without adding any points to your overall total.\nReady to play? (type yes/no)")

    flag = 0
    while flag == 0:
        answer = inputFunction()
        if isYes(answer):
            flag = 1
            start_game(outputFunction, inputFunction)
        elif isNo(answer):
            flag = 1
            outputFunction("Maybe another time!")
        else:
            outputFunction("I'm sorry, I didn't catch that.\nReady to play? (type yes/no)")

def start_game(outputFunction, inputFunction):
    humanScore = 0
    computerScore = 0
    outputFunction("\n------------------------------\nAlright! Let's start.\nWould you like to go first? (type yes/no)")

    flag = 0
    computerFirst = False
    game_end = False
    while flag == 0:
        answer = inputFunction()
        if isYes(answer):
            flag = 1
            outputFunction("You will start\n")
        elif isNo(answer):
            flag = 1
            computerFirst = True
            outputFunction("I will start\n")
            computerScore += computerTurn(outputFunction, inputFunction)
            outputFunction("I end my turn with a score of " + str(computerScore) + "\n")
            time.sleep(1)
            if computerScore >= 100:
                outputFunction("That means I win!")
                game_end = True
        else:
            outputFunction("I'm sorry, I didn't catch that.\nWould you like to go first? (type yes/no)")

    while not game_end:
        humanScore += humanTurn(outputFunction, inputFunction)
        outputFunction("You end your turn with a score of " + str(humanScore) + "\n")
        if humanScore >= 100:
            outputFunction("That means you win! Congrats!")
            game_end = True
        else:
            computerScore += computerTurn(outputFunction, inputFunction)
            outputFunction("I end my turn with a score of " + str(computerScore) + "\n")
            time.sleep(1)
            if computerScore >= 100:
                outputFunction("That means I win!")
                game_end = True

def humanTurn(outputFunction, inputFunction):
    turnScore = 0
    outputFunction("Your turn\n-----")
    endTurn = 0
    while endTurn == 0:
        dieRoll = rollDie()
        if dieRoll != 1:
            turnScore += dieRoll
            outputFunction("You rolled a " + str(dieRoll) + ".\nYour score for this turn is " + str(turnScore) + "\nRoll again? (type yes/no)")
            
            chosen = 0
            while chosen == 0:
                choice = inputFunction()
                if isYes(choice):
                    outputFunction("\n")
                    chosen = 1
                elif isNo(choice):
                    outputFunction("\n")
                    chosen = 1
                    endTurn = 1
        elif dieRoll == 1:
            turnScore = 0
            outputFunction("You rolled a 1! You lose all of the points you accumulated this turn. :(")
            endTurn = 1
    return turnScore

def computerTurn(outputFunction, inputFunction):
    turnScore = 0
    outputFunction("My turn\n-----")
    endTurn = 0
    while endTurn == 0:
        time.sleep(1)
        dieRoll = rollDie()
        if dieRoll != 1:
            turnScore += dieRoll
            outputFunction("I rolled a " + str(dieRoll) + ".\nMy score for this turn is " + str(turnScore))
            time.sleep(1)
            if random.random() >= .25:
                outputFunction("I'll roll again.\n")
            else:
                outputFunction("I'll end my turn.\n")
                time.sleep(1)
                endTurn = 1
        elif dieRoll == 1:
            turnScore = 0
            outputFunction("I rolled a 1! I lose all of the points I accumulated this turn. :(")
            endTurn = 1
    return turnScore

def isYes(inp):
    if (inp == "y" or inp == "Y" or inp == "yes" or inp == "Yes"):
        return True

def isNo(inp):
    if (inp == "n" or inp == "N" or inp == "no" or inp == "No"):
        return True

def rollDie():
    roll = random.random()
    roll *= 6
    roll = math.ceil(roll)
    return int(roll)

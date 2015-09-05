import socket
import time
import sys
import cPickle
import hashlib
import logging
import urllib2
import fileutil
import os

from fcmlimage import FCMLImage
from random import randint
from fileutil import FormattedFCML

hashedShutdownPassword = '1cd024d7d690559cb63a8fc33173ad3e76233c7843a131ca98250dc9a984253bdc586e0069261881ce1cbd30e51a98888740f8bcfcb342e453bc17bed1e64363'
hashedAuthenticationPassword = '94400a69906fd91b63cfae3066e1e90a6c8d2c506f473a61449a419260d3d72f1d95242ad644cc38f80703247dd17b7bd42062e24e54545b7159e2f84b794050'
server = 'polar.coldfront.net'
channel = '#fctest'
nick = 'marian'
passw = 'iamafantasticcontraptionbot'
port = 6667
ircsock = socket.socket()
shufflePath = "shuffle.p"
hellomessages = ['How you doin there, {name}?', 'Sup, {name}?', 'You must be {name}.', 'Well, if it isn\'t {name}.']
sandwichmessages = ['You do not have administrator privileges to request a sandwich.', 'No, you sexist.', 'Aww, {name} doesn\'t know how to make a sandwich?']
sudomessages = ["Yep! One {nick} coming right up!", "Well, {name}, since you insist.", "Since you asked so nicely, sure!", "Would you like ketchup with that?"]
whitelist = []

ircsock.connect((server, port))
ircsock.send("PASS " + passw + "\r\n")
ircsock.send("NICK " + nick + "\r\n")
ircsock.send("USER " + nick + " " + nick + " " + nick + " : This is marian, a Fantastic Contraption IRC bot - Type !help to see how marian can help you.\r\n")

commands = []; #List of possible commands
               #Each element is a tuple in the form of [command name, command description, callback function, displayInHelp]
               #Add commands with newCommand(name, description, callback, display) and if display is True, it shows in help, and viceversa

class Shuffle(object):
   def __init__(self, level, entryNumber):
      print "Init is called"
      self.entryNumber = entryNumber
      self.checkLevel(level)
      self.level = level
      self.solution = ""
      self.name = ""

   def __repr__(self):
      if self.hasSolution():
         return self.level + " has solution " + self.solution + " by " + self.name
      else:
         return self.level + " has no solution"

   def checkLevel(self, level):
      # We should check to see that it's a valid level url, or even just in the right format
      return True

   def checkSolution(self, solution):
      return True

   def solveLevel(self, solution, username):
      self.solution = solution
      self.name = username

   def hasSolution(self):
      try:
         return self.solution != ""
      except Exception:
         return False

# Get the shuffle data
shuffles = []
try:
   shuffles = cPickle.load(open(shufflePath, "rb"))
except Exception as e:
   print(e)

def main():
   #Here the commands are added
   addCommand("help", "Displays this command dialog.", displayHelp, True)
   addCommand("quit", "Causes the bot to quit. Be prepared to authenticate with a password.", quitIRC, False)
   addCommand("shuf", "Access the ChatShuffle2.0", shuf, True)
   addCommand("count", "Get the piece count for a design ID", count, True)
   addCommand("levelfcml", "Exports a level to fcml", levelfcml, True)
   addCommand("designfcml", "Exports a design to fcml", designfcml, True)
   addCommand("imageify", "Generates fcml given an image url // WORK IN PROGRESS", imageify, True)
   addCommand("auth", "Administrator authentication", auth, False)
   addCommand("deauth", "Remove name from whitelist", deauth, False)
   addCommand("randLevel", "Gets a random level. Can specify [unsolved]", randLevel, True)
   
   #Easter Eggs
   addCommand("marian", "Easter Egg", marian, False)
   addCommand("hello", "Easter Egg", hello, False)
   addCommand("sandwich", "Easter Egg", sandwich, False)
   addCommand("sudosandwich", "Easter Egg", sudosandwich, False)
   addCommand("sudo", "Easter Egg", sudo, False)

   logging.basicConfig(format='%(asctime)s %(message)s', filename='HTMLsaves/irclog.log', level=logging.WARNING)

   while True:
      data = ircsock.recv(2048)
      print (data)

      if data.find("PING") != -1:
         ircsock.send("PONG :" + data.split(':')[1])
         print("I ponged back")
      elif data.find("Nickname is already in use") != -1:
         print("Quiting")
         sys.exit()
      elif data.find("you are now recognized") != -1:
         print("Trying to join channel " + channel + " now")
         sendmsg(channel, "Hellooo") #This never actualy gets sent but it seems necessary to have this line here because otherwise the bot won't join the channel. Not sure why.
         ircsock.send('JOIN :' + channel + '\r\n')
         sendmsg(channel, "Hello everyone! I am a Marian version beta! Type !help to see my list of commands. Beep Boop.")
      else:
         try:
            parsemessage(data, ircsock, channel)
         except Exception as e:
            print "Message could not be parsed"
            print e
 
def parsemessage(data, ircsock, channel):
   msgParts = data.split(':', 2)
   cmd = msgParts[2]
   name = ""

   try:
      name = msgParts[1].split('!')[0]
   except Exception:
      logging.warning('Message sent but no name found!')
   logging.info(name + ": " + cmd)

   if cmd[0] == '!':
      print name + " | sent this message"
      source = (msgParts[1].split())[2]
      
      if source == nick: #If it was a private message to the bot
         destination = name #Respond to the sender
      else:
         destination = source #Otherwise, send it back where it came from (the channel)
         
      cmdparts = cmd[1:].split()
 
      tup = findCommandTuple(cmdparts[0])
      if (tup == False):
         sendmsg(destination, "I'm sorry, I didn't catch that.") #Or maybe if the command isn't found it should just do nothing

      else:
         tup[2](cmdparts, name, destination) #If it is found, then run the callback function located at index 2
                      #Pass name and cmdparts, and destination

def randomitemfrom(alist):
   return alist[randint(0, len(alist) - 1)]

def log(message, name):
   pass

##def sendmsgtofc(msg):
##   sendmsg("#fctest", msg)
   
def sendmsg(dest, msg, name = "<insert name>", nick = "<insert nick>"): # This is the send message function, it sends messages to the channel.
   msg = reverseEscape(msg, name, nick)  #The function will escape certain special markup
   ircsock.send("PRIVMSG "+ dest +" :"+ msg +"\n")

def addCommand(name, description, callback, display):
   commands.append((name, description, callback, display))

def findCommandTuple(name):
   for command in commands:
      if command[0].upper() == name.upper():
         return command
 
   return False #If nothing was found, it will get to here, where it will return False
 
def reverseEscape(message, name, nick): #Not sure what to call it, feel free to rename this function
   string = message
   string = string.replace("{name}", name)
   string = string.replace("{nick}", nick)
   return string

#Hopefully, a master function for waiting for and taking input
def getInput(name):
   #Now run an infinite loop to halt the code that called this function until input can be returned
   inputRecieved = False
   while inputRecieved == False:
      data = ircsock.recv(2048)
      msgParts = data.split(':', 2)
      cmd = msgParts[2]
      sourceName = msgParts[1].split('!')[0]
      if sourceName == name:
         return cmd
   
#COMMAND CALLBACK FUNCTIONS after this point
#All functions get passed name, MAKE SURE THEY ALL INCLUDE A PARAMETER FOR NAME
#same thing for args and destination
#Then make sre messages are sent to the correct destination
def displayHelp(args, name, destination):
   #I'm sure there is some sort of printf for easy formating, but I rather do it manually
   sendmsg(destination, "List of commands you can use:")
   for command in commands:
      if command[3]:
         sendmsg(destination, "    !" + command[0] + " | " + command[1])

def getWhitelist():
   return whitelist

def getShuffles():
   return shuffles

# For some reason python is not finding the variable whitelist, even though it is
# defined at the top of this file.  I've tried making the variable global with no success.
# If you get a change, investigate this issue pls? :-)
def auth(args, name, destination):
   try:
      whitelist = getWhitelist()
      if len(args) == 2:
         if args[1] == 'get-all':
            if len(whitelist) != 0:
               sendmsg(destination, "Whitelisted users:")
               for name in whitelist:
                  sendmsg(destination, "> " + name)
            else:
               sendmsg(destination, "No users have administrator privileges.")
            return
         hashedPass = hashlib.sha512(args[1] + "saltauthsaltauthsalt").hexdigest()
         if hashedPass == hashedAuthenticationPassword:
            if name not in whitelist:
               whitelist += [name]
               sendmsg(destination, "Password confirmed, you've been whitelisted.")
               sendmsg(destination, "> You will remain whitelisted until you log out.")
               sendmsg(destination, "> Remember to log out before you leave using '!deauth'")
               return
            else:
               sendmsg(destination, "You area already logged in.")
               return
   except Exception as e:
      print(e)
   sendmsg(destination, "Invalid password!")

def deauth(args, name, destination):
   try:
      if name in whitelist:
         whitelist.remove(name)
         sendmsg(destination, "You've been removed from the whitelist")
      else:
         sendmsg(destination, "You are not whitelisted. Try 'auth get-all' to see whitelist.")
   except Exception as e:
      print(e)

def quitIRC(args, name, destination):
##   if (name == "rian" or name == "marjo"): #We may have to expand this to a full whitelist later
##      print("Leaving")                     #Also at the moment it is just based on nicks
##      sendmsg(destination, "Goodbye!")
##      ircsock.send('QUIT\r\n')
##      sys.exit(name)

   #Ok, the whitelist is bugging out and not letting me quit. Let's leave that for later
   if name in whitelist:
      print("Leaving")
      sendmsg(channel, "Goodbye!") #Say to the whole channel marian is leaving
      ircsock.send('QUIT\r\n')
      sys.exit(name)
   sendmsg(destination, "You do not have admin privileges.")

def marian(args, name, destination):
   sendmsg(destination, "Yes? Can I help you?")

def hello(args, name, destination):
   sendmsg(destination, randomitemfrom(hellomessages), name)

def shuf(args, name, destination):
   shuffles = getShuffles()
   if len(args) < 2:
      displayShufRules(destination)
      return
   if args[1] == 'solve' and len(args) == 3:
      if len(shuffles) > 0:
         if shuffles[-1].hasSolution():
            sendmsg(destination, "Shuf #" + str(len(shuffles)) + " already has a solution. Please edit.")
         else:
            if not "http://FantasticContraption.com/?designId=" in args[2]:
               sendmsg(destination, "This design is not in the correct design format")
               return
            shuffles[-1].solveLevel(args[2], name)
            f = open(shufflePath, "wb")
            cPickle.dump(shuffles, f)
            f.close()
            solvedlevel = shuffles[-1].level.replace("level", "edit")
            sendmsg(destination, "Nice solve! Edit link:")
            sendmsg(destination, solvedlevel)
      else:
         sendmsg(destination, "There is no level to be solved. Make the first level! Do 'shuf edit [URL]'")
   elif args[1] == 'edit' and len(args) == 3:
      if len(shuffles) > 0:
         if not shuffles[-1].hasSolution():
            sendmsg(destination, "You have to solve the other level first, silly.")
            sendmsg(destination, shuffles[-1].level)
            return
      if not "http://FantasticContraption.com/?levelId=" in args[2]:
         sendmsg(destination, "This level is not in the correct level format")
         return
      shuffles.append(Shuffle(args[2], len(shuffles) + 1))
      f = open(shufflePath, "wb")
      cPickle.dump(shuffles, f)
      f.close()
      sendmsg(channel, "Level added")
   elif args[1] == 'level':
      if len(shuffles) == 0:
         sendmsg(destination, "No levels in database.")
      elif not shuffles[-1].level:
         sendmsg(destination, "Last level could not be found.")
      else:
         sendmsg(destination, shuffles[-1].level)
   elif args[1] == 'last' and len(args) == 2:
      try:
         if shuffles[-1].solution != "":
            sendmsg(destination, str(shuffles[-1]))
         elif shuffles[-2].solution != "":
            sendmsg(destination, str(shuffles[-2]))
         else:
            sendmsg(destination, "Something went wrong.")
      except Exception:
         sendmsg(destination, "No solution could be found.")
   elif args[1] == 'find' and len(args) == 3:
      try:
         solutionNum = int(args[2])
         sendmsg(destination, str(shuffles[solutionNum - 1]))
      except Exception:
         sendmsg(destination, "Entry doesn't exist or invalid syntax.")
   elif args[1] == 'rules':
      displayShufRules(destination)
   elif args[1] == 'clear': 
      if name in whitelist:
         try:
            shuffles = []
            f = open(shufflePath, "wb")
            cPickle.dump(shuffles, f)
            f.close()
            sendmsg(destination, "Shuffle database deleted. This action cannot be undone. Oh well. Too late.")
         except Exception as e:
            sendmsg(destination, "Shuffle files probably corrupted. Way to go.")
            print e
      else:
         sendmsg(destination, "You are not cleared to perform this action")
   else:
      sendmsg(destination, "Invalid command syntax.")

def displayShufRules(destination):
   sendmsg(destination, "Chat Shuffle 2.0: Easy-Moderate difficulty.")
   sendmsg(destination, "-- View the current level: '!shuf level'")
   sendmsg(destination, "-- Solve the current level: '!shuf solve [designID]'")
   sendmsg(destination, "-- Edit the current level: '!shuf edit [levelID]'")
   sendmsg(destination, "-- Find a particular level/solution: '!shuf find [index]'")

def imageify(args, name, destination):
   # Check against a clock so that marian doesn't get spammed. (Once every minute?)
   try:
      if len(args) >= 2:
         imageURL = args[1]
         xtrans = 0
         ytrans = 0
         scale = 1
         sens = 550
         if len(args) > 2:
            for arg in args:
               opt = arg.split("=")
               if len(opt) != 2:
                  sendmsg(destination, "Invalid args! Possible args:")
                  sendmsg(destination, "xtrans, ytrans, scale")
                  return
               if opt[0] == "xtrans":
                  xtrans = int(opt[1])
                  if xtrans > 1100 or xtrans < -1100:
                     sendmsg(destination, "Your xtrans value must be within -1100 and 1100")
                     return
               if opt[0] == "ytrans":
                  ytrans = int(opt[1])
                  if ytrans > 1100 or ytrans < -1100:
                     sendmsg(destination, "Your ytrans value must be within -1100 and 1100")
                     return
               if opt[0] == "scale":
                  scale = float(opt[1])
                  if scale > 10 or scale < 0.1:
                     sendmsg(destination, "Your scale must be within 0.1 and 10")
                     return
               if opt[0] == "sensitivity":
                  sens = int(opt[1])
                  if sens <= 0:
                     sendmsg(destination, "Your sensitivity must be greater than 0")
                     return
         fcmlImage = FCMLImage(imageURL, xtrans, ytrans, scale, sens)
         fcml = fcmlImage.partition()
         # ---------------------------------
         # Do something clever with the fcml
         # ---------------------------------
         formattedfcml = FormattedFCML("newfile")
         formattedfcml.writeToFile(fcml)
         sendmsg(destination, formattedfcml.filePath)

   except Exception as e:
      # sendmsg(destination, "Something went wrong with your input")
      sendmsg(destination, "This feature is not yet implemented. Hang tight.")
      print(e)

def count(args, name, destination):
   try:
      if len(args) == 2:
         designID = args[1].strip()
         if "design" in designID:
            designID = designID[designID.index("=") + 1:]
         else:
            designID = args[1]
         url = urllib2.urlopen("http://fc.sk89q.com/design?designId=" + designID)
         html = url.read()
         countLocation1 = html.rfind("<th>Total:</th>") + 20
         countLocation2 = html.index("</td>", countLocation1)
         pieceCount = "Piece count for ID=" + designID + ": " + html[countLocation1 : countLocation2]
         if len(pieceCount) > 31:
            raise Exception("this user is an idiot")
         sendmsg(destination, pieceCount)
      else:
         sendmsg("Invalid syntax")
   except Exception as e:
      sendmsg(destination, "Bad input")
      print(e)

def levelfcml(args, name, destination):
   try:
      if len(args) == 2:
         levelID = args[1].strip()
         if "level" in levelID:
            levelID = levelID[levelID.index("=") + 1:]
         else:
            levelID = args[1].strip()
         int(levelID)
         url = "http://fc.sk89q.com/export?type=level&id={name}&format=fcml"
         sendmsg(destination, url, levelID)
   except Exception as e:
      sendmsg("Invalid levelID")

def designfcml(args, name, destination):
   try:
      if len(args) == 2:
         designID = args[1].strip()
         if "design" in designID:
            designID = designID[designID.index("=") + 1:]
         else:
            designID = args[1].strip()
         int(designID)
         url = "http://fc.sk89q.com/export?type=design&id={name}&format=fcml"
         sendmsg(destination, url, designID)
   except Exception as e:
      sendmsg("Invalid designID")

def inputTest(args, name, destination):
   sendmsg(destination, "{name} must now send input", name)
   inp = getInput(name)
   sendmsg(destination, "Input from {name}: " + inp, name)

def sandwich(args, name, destination):
   sendmsg(destination, randomitemfrom(sandwichmessages), name)

def sudosandwich(args, name, destination):
   sendmsg(destination, ".......ok... :(")

def sudo(args, name, destination):
   if name in whitelist:
      if args == ["sudo", "rm", "-rf", "/"]:
         sendmsg(destination, "MARIAN SELFDESTRUCT SEQUENCE IN")
         sendmsg(destination, "3...")
         time.sleep(1)
         sendmsg(destination, "2...")
         time.sleep(1)
         sendmsg(destination, "1...")
         time.sleep(1)
         sendmsg(destination, "KABOOM!!!!!!!!!!!!!!!!!!!!")
         sendmsg(destination, "<blue_screen_of_death>")
      elif len(args) >= 2:
         item = " ".join(args[1:])
         sendmsg(destination, randomitemfrom(sudomessages), name=name, nick=item)
      else:
         sendmsg(destination, "You need to ask for something.")
   else:
      sendmsg(destination, "Hah!! Who do you think YOU are?!")

def randLevel(args, name, destination):
   #let's start with the level purge as our lowest point
   lowPoint = 489000 #This is about where I found the first level

   #To find the high point, we need to see the latest created ID
   #We could do this by visiting http://www.fantasticcontraption.com/saveLevel.php
   #And simply reading off the number, but I don't want to polute the game
   #with blank levels. Instead, let's go to http://fc.sk89q.com/levels?difficulty=0&sort=date&order=DESC
   #and read off the first number. For now, let's just assume the number is 636000
   highPoint = 636000
   try:
      url = urllib2.urlopen("http://fc.sk89q.com/levels?difficulty=0&sort=date&order=DESC")
      html = url.read()
      firstLevelStartIndex = html.index("http://fantasticcontraption.com/?levelId=")
      firstIDStartIndex = html.index("=", firstLevelStartIndex) + 1
      firstIDEndIndex = html.index("\"", firstIDStartIndex)
      highPoint = int(html[firstIDStartIndex : firstIDEndIndex])
      print highPoint
   except Exception as e:
      sendmsg(destination, "The resource is down. Here's what I can do:")

   randID = randint(lowPoint, highPoint)
   url = urllib2.urlopen("http://fc.sk89q.com/level?levelId=" + str(randID))
   #We should check to make sure the level is published. If it is not, we should find another level
   #Got a flue shot today and it hurts so I am not in the mood right now
   
   html = url.read()
   nameLocation1 = html.rfind("<strong>Level name:</strong>") + 29
   nameLocation2 = html.index("</li>", nameLocation1)
   levelName = html[nameLocation1 : nameLocation2]

   authorLocation1 = html.rfind("<strong>Authored by:</strong>") + 30
   authorLocation1 = html.index(">", authorLocation1) + 1
   authorLocation2 = html.index("</li>", authorLocation1) - 5
   levelAuthor = html[authorLocation1 : authorLocation2] #Finding author still needs some work
   
   sendmsg(destination, levelName + " by " + levelAuthor + ": www.fantasticcontraption.com/?levelId=" + str(randID))

main()

import socket
import time
import sys
import cPickle
import pig
import hashlib
import logging
import urllib2
 
from random import randint

hashedShutdownPassword = '1cd024d7d690559cb63a8fc33173ad3e76233c7843a131ca98250dc9a984253bdc586e0069261881ce1cbd30e51a98888740f8bcfcb342e453bc17bed1e64363'
server = 'polar.coldfront.net'
channel = '#fctest'
nick = 'marian'
passw = 'iamafantasticcontraptionbot'
port = 6667
ircsock = socket.socket()
shufflePath = "shuffle.p"
hellomessages = ['How you doin there, {name}?', 'Sup, {name}?', 'You must be {name}.', 'Well, if it isn\'t {name}.']
sandwichmessages = ['You do not have administrator privileges to request a sandwich.', 'No, you sexist.', 'Aww, {name} doesn\'t know how to make a sandwich?']

ircsock.connect((server, port))
ircsock.send("PASS " + passw + "\r\n")
ircsock.send("NICK " + nick + "\r\n")
ircsock.send("USER " + nick + " " + nick + " " + nick + " : This is a bot that I really really hope will work\r\n")

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
   addCommand("marian", "Say hello!", marian, False) #This command probably should not be included in !help
   addCommand("hello", "I will greet you.", hello, False) #This command probably should not be included in !help
   addCommand("shuf", "Access the ChatShuffle2.0", shuf, True)
   addCommand("count", "Get the piece count for a design ID", count, True)
   addCommand("inputTest", "test for input", inputTest, False)
   addCommand("sandwich", "Easter Egg", sandwich, False)
   addCommand("sudosandwich", "Easter Egg", sudosandwich, False)

   logging.basicConfig(format='%(asctime)s %(message)s', filename='irclog.log', level=logging.DEBUG)

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
         parsemessage(data, ircsock, channel)
 
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

def quitIRC(args, name, destination):
##   if (name == "rian" or name == "marjo"): #We may have to expand this to a full whitelist later
##      print("Leaving")                     #Also at the moment it is just based on nicks
##      sendmsg(destination, "Goodbye!")
##      ircsock.send('QUIT\r\n')
##      sys.exit(name)

   #Ok, the whitelist is bugging out and not letting me quit. Let's leave that for later
   if len(args) == 2:
      hashedPass = hashlib.sha512(args[1] + "thisissomesaltforthepasswordlala").hexdigest()
      if hashedPass == hashedShutdownPassword:
         sendmsg(destination, "Password confirmed, shutting down.")
         print("Leaving")
         sendmsg(channel, "Goodbye!") #Say to the whole channel marian is leaving
         ircsock.send('QUIT\r\n')
         sys.exit(name)
   sendmsg(destination, "Invalid password!")
 
def marian(args, name, destination):
   sendmsg(destination, "Yes? Can I help you?")

def hello(args, name, destination):
   sendmsg(destination, randomitemfrom(hellomessages), name)

def shuf(args, name, destination):
   if len(args) < 2:
      sendmsg(destination, "blah blah syntax error, show shuf options, blah")
      return
   if args[1] == 'solve' and len(args) == 3:
      if len(shuffles) > 0:
         if shuffles[-1].hasSolution():
            sendmsg(destination, "Shuf #" + str(len(shuffles)) + " already has a solution. Please edit.")
         else:
            shuffles[-1].solveLevel(args[2], name)
            f = open(shufflePath, "wb")
            cPickle.dump(shuffles, f)
            f.close()
            sendmsg(destination, "Nice solve! Database updated. Remember to edit!")
      else:
         sendmsg(destination, "There is no level to be solved. Make the first level! Do 'shuf edit [URL]'")
   elif args[1] == 'edit' and len(args) == 3:
      if len(shuffles) > 0:
         if not shuffles[-1].hasSolution():
            sendmsg(destination, "You have to solve the other level first, silly.")
            sendmsg(destination, shuffles[-1].level)
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
   else:
      sendmsg(destination, "Invalid command syntax.")

def count(args, name, destination):
   try:
      if len(args) == 2:
         designID = args[1]
         url = urllib2.urlopen("http://fc.sk89q.com/design?designId=" + designID)
         html = url.read()
         countLocation1 = html.rfind("<th>Total:</th>") + 20
         countLocation2 = html.index("</td>", countLocation1)
         pieceCount = "Piece count for ID=" + designID + ": " + html[countLocation1 : countLocation2]
         sendmsg(destination, pieceCount)
   except Exception as e:
      print(e)

def playPig(args, name, destination):
   #We don't want to play a game in the mian channel, it will annoy people
   #Therefore, first check to see if this is a private conversation
   #If name == destination, then it is a private conversation
   if (name ==  destination):
      pass
   else:
      sendmsg(destination, "I am sorry {name}, you can only play that game in a private chat with me. Type \"/query {nick} !pig\" to play.", name, nick)

def inputTest(args, name, destination):
   sendmsg(destination, "{name} must now send input", name)
   inp = getInput(name)
   sendmsg(destination, "Input from {name}: " + inp, name)

def sandwich(args, name, destination):
   sendmsg(destination, randomitemfrom(sandwichmessages), name)

def sudosandwich(args, name, destination):
   sendmsg(destination, ".......ok... :(")

main()

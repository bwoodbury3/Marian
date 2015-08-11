import socket
import time
import sys
import cPickle
 
from random import randint
 
server = 'polar.coldfront.net'
channel = '#fctest'
nick = 'marian'
passw = 'iamafantasticcontraptionbot'
port = 6667
ircsock = socket.socket()
shufflePath = "shuffle.p"
hellomessages = ['How you doin there, {name}?', 'Sup, {name}?', 'You must be {name}.', 'Well, if it isn\'t {name}.']

ircsock.connect((server, port))
ircsock.send("PASS " + passw + "\r\n")
ircsock.send("NICK " + nick + "\r\n")
ircsock.send("USER " + nick + " " + nick + " " + nick + " : This is a bot that I really really hope will work\r\n")

commands = []; #List of possible commands
               #Each element is a tuple in the form of [command name, command description, callback function]
               #Add commands with newCommand(name, description, callback)

class Shuffle(object):
   def __init__(self, level, entryNumber):
      self.entryNumber = entryNumber
      print "Init is called"
      self.checkLevel(level)
      self.level = level
      self.solution = ""
      self.name = ""

   def __repr__(self):
      if self.hasSolution():
         return "#" + str(self.entryNumber) + ": " + self.level + " has solution " + self.solution + " by " + self.name
      else:
         return "#" + str(self.entryNumber) + ": " + self.level + " has no solution"

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
   addCommand("help", "Displays this command dialog.", displayHelp)
   addCommand("quit", "Causes the bot to quit. Be prepared to authenticate with a password.", quitIRC)
   addCommand("marian", "Say hello!", marian) #This command probably should not be included in !help
   addCommand("hello", "I will greet you.", hello) #This command probably should not be included in !help
   addCommand("shuf", "Access the ChatShuffle2.0", shuf)

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
   print cmd + " | is the command"
   if cmd[0] == '!':
      name = msgParts[1].split('!')[0]
      print name + " | sent this message"
      cmdparts = cmd[1:].split()
 
      tup = findCommandTuple(cmdparts[0])
      if (tup == False):
         sendmsg(channel, "I'm sorry, I didn't catch that.") #Or maybe if the command isn't found it should just do nothing

      else:
         tup[2](cmdparts, name) #If it is found, then run the callback function located at index 2
                      #Pass name cuz why not, some functions will use it

def randomitemfrom(alist):
   return alist[randint(0, len(alist) - 1)]
 
def sendmsgtofc(msg):
   sendmsg("#fctest", msg)
   
def sendmsg(chan, msg, name = "<insert name>"): # This is the send message function, it sends messages to the channel.
   msg = reverseEscape(msg, name)  #The function will escape certain special markup
   ircsock.send("PRIVMSG "+ chan +" :"+ msg +"\n")

def addCommand(name, description, callback):
   commands.append((name, description, callback))

def findCommandTuple(name):
   for command in commands:
      if command[0] == name:
         return command
 
   return False #If nothing was found, it will get to here, where it will return False
 
def reverseEscape(message, name):
   string = message
   string = string.replace("{name}", name)
   return string

#COMMAND CALLBACK FUNCTIONS after this point
#All functions get passed name, MAKE SURE THEY ALL INCLUDE A PARAMETER FOR NAME
def displayHelp(args, name):
   #I'm sure there is some sort of printf for easy formating, but I rather do it manually
   sendmsg(channel, "List of commands you can use:")
   for command in commands:
      sendmsg(channel, "    !" + command[0] + " | " + command[1])

def quitIRC(args, name):
   print("Leaving")
   sendmsg(channel, "Goodbye!")
   ircsock.send('QUIT\r\n')
   sys.exit(name)
 
def marian(args, name):
   sendmsg(channel, "Yes? Can I help you?")

def hello(args, name):
   sendmsg(channel, randomitemfrom(hellomessages), name)

def shuf(args, name):
   if len(args) < 2:
      sendmsg(channel, "blah blah syntax error, show shuf options, blah")
      return
   if args[1] == 'solve' and len(args) == 3:
      if len(shuffles) > 0:
         if shuffles[-1].hasSolution():
            sendmsg(channel, "Shuf #" + str(len(shuffles)) + " already has a solution. Please edit.")
         else:
            shuffles[-1].solveLevel(args[2], name)
            f = open(shufflePath, "wb")
            cPickle.dump(shuffles, f)
            f.close()
            sendmsg(channel, "Nice solve! Database updated. Remember to edit!")
      else:
         sendmsg(channel, "There is no level to be solved. Make the first level! Do 'shuf edit [URL]'")
   elif args[1] == 'edit' and len(args) == 3:
      if len(shuffles) > 0:
         if not shuffles[-1].hasSolution():
            sendmsg(channel, "You have to solve the other level first, silly.")
            sendmsg(channel, shuffles[-1].level)
            return
      shuffles.append(Shuffle(args[2], len(shuffles) + 1))
      f = open(shufflePath, "wb")
      cPickle.dump(shuffles, f)
      f.close()
      sendmsg(channel, "Level added")
   elif args[1] == 'level':
      if len(shuffles) == 0:
         sendmsg(channel, "No levels in database.")
      elif not shuffles[-1].level:
         sendmsg(channel, "Last level could not be found.")
      else:
         sendmsg(channel, shuffles[-1].level)
   elif args[1] == 'last' and len(args) == 2:
      try:
         if shuffles[-1].solution != "":
            sendmsg(channel, str(shuffles[-1]))
         elif shuffles[-2].solution != "":
            sendmsg(channel, str(shuffles[-2]))
         else:
            sendmsg(channel, "Something went wrong")
      except Exception:
         sendmsg(channel, "No solution could be found.")
   elif args[1] == 'find' and len(args) == 3:
      try:
         solutionNum = int(args[2])
         sendmsg(channel, str(shuffles[solutionNum - 1]))
      except Exception:
         sendmsg(channel, "Entry doesn't exist or invalid syntax.")
   else:
      sendmsg(channel, "Invalid command syntax.")

main()
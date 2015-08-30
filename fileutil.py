import os

def createHTMLFile(fileName, fileContent): #returns link
    currentDirectory = os.getcwd() + "/HTMLsaves/"
    newFile = open(currentDirectory + fileName + ".html", 'w')
    newFile.write(fileContent)
    url = currentDirectory + newFile.name
    return url

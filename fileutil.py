import os

def createHTMLFile(fileName, fileContent): #returns link
    newFileName = os.getcwd() + "/HTMLsaves/" + fileName + ".html"
    newFile = open(newFileName, 'w')
    newFile.write(fileContent)
    url = newFileName
    return url

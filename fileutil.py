def createHTMLFile(fileName, fileContent): #returns link
    newFile = open(fileName + ".html", 'w')
    newFile.write(fileContent)
    url = "file:///C:/Users/Joseph/Documents/Programming/Python/AI/Marian/HTMLsaves/" + newFile.name
    return url

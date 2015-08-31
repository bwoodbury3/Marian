import os

class FormattedFCML:
   def __init__(self, fileName): #returns link
      self.filePath = os.getcwd() + "/HTMLsaves/" + fileName + ".html"

   def writeToFile(self, fcml):
      fcml = fcml.replace("\n", "<br>")
      header = "; This code was exported by Marian<br><br>"
      title = "@name        Exported<br>"\
              "@description Exported code by marian<br><br>"
      areas = "; Build and goal areas<br>"\
              "BuildArea (-200, 0), (200, 200), 0<br>"\
              "GoalArea (200, 0), (200, 200), 0<br><br>"
      objs = "; Level objects<br>" + fcml + "<br><br>"
      goals = "; Goal and design objects<br>"\
              "GoalCircle#0 (0, 0), (40, 40)<br>"

      finalhtml = header + title + areas + objs + goals
      htmlFile = open(self.filePath, 'w')
      htmlFile.write(finalhtml)
      htmlFile.close()

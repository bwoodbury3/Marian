import math

class Equation:
    global numbers
    numbers = "1234567890xn.E"
        # A couple of notes about accepted values:
        #   'x' is a variable, of which one variable is allowed
        #   'n' is a negative sign, to differentiate it from a minus sign
    global operators
    operators = "+-*/^!"
    
    def __init__(self, userinput):
        self.strEquation = userinput
        self.userinput = userinput
        self.values, self.symbols = self.toArrays()

    def __str__(self):
        return self.strEquation

    def toArrays(self):
        self.userinput = self.userinput.replace(" ", "")
        subequations = []
        values = []
        symbols = []

        parenstack = []
        if "(" in self.userinput:
            userinputOld = self.userinput
            self.userinput = ""
            for i in range(0, len(userinputOld)):
                self.userinput += userinputOld[i]
                if userinputOld[i] == "(":
                    parenstack.append(i)
                elif userinputOld[i] == ")":
                    index = parenstack.pop()
                    if len(parenstack) == 0:
                        subequations.append(Equation(userinputOld[index + 1 : i]))
                        self.userinput = self.userinput.replace(userinputOld[index : i + 1], "E")

        currNumber = ""
        index = 0
        for char in self.userinput:
            if char in numbers:
                if char == "E":
                    values.append(subequations[index])
                    index += 1
                else:
                    currNumber += char
            elif char in operators:
                symbols.append(char)
                if currNumber != "":
                    if currNumber.startswith("n"):
                        values.append(-1 * float(currNumber[1:]))
                    elif currNumber == 'x':
                        values.append('x')
                    else:
                        values.append(float(currNumber))
                currNumber = ""
        if currNumber != "": # at the end of the iterations, we might have one trailing character
            if currNumber == 'x':
                values.append('x')
            else:
                values.append(float(currNumber))
        return (values, symbols)

    def evaluate(self, x):
        index = 0
        values = self.values[:]
        symbols = self.symbols[:]
        for i in range(len(values)): # recursive step: replace each class instance with 
            if isinstance(values[i], Equation):
                values[i] = values[i].evaluate(x)
                index += 1
            if values[i] == 'x':
                values[i] = x

        while "!" in symbols:
            i = symbols.index("!")
            sol = math.factorial(values[i])
            values[i] = sol
            symbols = symbols[: i] + symbols[i + 1 :]

        while "^" in symbols:
            i = symbols.index("^")
            sol = values[i] ** values[i + 1]
            values = values[0 : i] + [sol] + values[i + 1 :]
            symbols = symbols[: i] + symbols[i + 1 :]

        while "*" in symbols:
            i = symbols.index("*")
            sol = values[i] * values[i + 1]
            values = values[0 : i] + [sol] + values[i + 1 :]
            symbols = symbols[: i] + symbols[i + 1 :]

        while "/" in symbols:
            i = symbols.index("/")
            sol = values[i] / values[i + 1]
            values = values[0 : i] + [sol] + values[i + 1 :]
            symbols = symbols[: i] +symbols[i + 1 :]

        while "+" in symbols:
            i = symbols.index("+")
            sol = values[i] + values[i + 1]
            values = values[0 : i] + [sol] + values[i + 1 :]
            symbols = symbols[: i] + symbols[i + 1 :]

        while "-" in symbols:
            i = symbols.index("-")
            sol = values[i] - values[i + 1]
            values = values[0 : i] + [sol] + values[i + 1 :]
            symbols = symbols[: i] + symbols[i + 1 :]

        return values[0]

class FCMLFunction:
    def __init__(self, equation, translateX=0, translateY=0, xScale=1, yScale=1, \
            xLeftBound=-1000, xRightBound=1000, numRects=100, width=10, recttype="DynamicRect"):
        if xLeftBound > xRightBound or xLeftBound < -1000 or xRightBound > 1000:
            raise Exception("Invalid boundaries")
        self.translateX = float(translateX)
        self.translateY = float(translateY)
        self.xScale = float(xScale)
        self.yScale = float(yScale)
        self.xLeftBound = float(xLeftBound)
        self.xRightBound = float(xRightBound)
        self.numRects = numRects
        self.equation = Equation(equation)
        self.width = width
        self.recttype = recttype

    def toFCML(self):
        #Divide function into equal segments
        virtualLeftBound = self.xLeftBound / self.xScale
        virtualRightBound = self.xRightBound / self.xScale
        delta = (virtualRightBound - virtualLeftBound) / self.numRects
        #Plotting loop
        lastX = (-1 * delta + virtualLeftBound)
        lastY = self.equation.evaluate(lastX) * self.yScale
        lastX = lastX * self.yScale
        fcml = ""
        for i in range(0, self.numRects):
            #The function must be first plotted normally, then translated to the user specs
            functionX = i * delta + virtualLeftBound
            functionY = self.equation.evaluate(functionX)
            x = functionX * self.xScale
            y = functionY * self.yScale
            slope = (y - self.equation.evaluate(functionX - 0.01) * self.yScale) / (0.01 * self.xScale)
            rotation = math.atan(-slope) #In radians
            size = math.sqrt((x - lastX) ** 2  + (y - lastY) ** 2) + 10
            lastX = x
            lastY = y
            block = self.plot(x, y, rotation, size)
            if block != "":
                fcml += self.plot(x, y, rotation, size) + "\n"
        return fcml

    def plot(self, x, y, rotation, size):
        if y < 725 and y > -725:
            return self.recttype + " (" + str(x) + ", " + str(-y) + "), (" + str(size) \
                + ", " + str(self.width) + "), " + str(int(rotation * 58))
        else:
            return ""


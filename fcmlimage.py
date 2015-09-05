import urllib
import cStringIO
from PIL import Image
import sys #for debugging; I might have forgotten to remove that

inf = 999999999

def dfs(G, vis, a, b): #maxSet's DFS
    vis[a] = True
    if a == b:
        return [a]

    if b in G[a] and G[a][b] != 0: #heuristic
        return [b, a]

    for i in G[a]:
        if not vis[i] and G[a][i] != 0:
            d = dfs(G, vis, i, b)
            if len(d) > 0:
                d.append(a)
                return d
    return []

def maxSet(V, vals):
    l = len(V)

    net = [{} for i in range(2 + 2*l)] #source = net[-1], sink = net[-2]
    for i in range(l): #network init
        net[-1][i] = vals[i][0]
        net[i][-1] = 0
        net[i+l][-2] = vals[i][1]
        net[-2][i+l] = 0      
   
        for j in V[i]:
            net[i][j+l] = inf
            net[j+l][i] = 0  

    vis = [False]*(2 + l*2)
    path = dfs(net, vis, -1, -2)

    while len(path) > 0: #ford-fulkerson algorithm
        m = inf
        for i in range(len(path)-1):
            m = min(net[path[i+1]][path[i]], m)

        for i in range(len(path)-1):
            net[path[i]][path[i+1]] += m
            net[path[i+1]][path[i]] -= m

        vis = [False]*(2 + l*2)
        path = dfs(net, vis, -1, -2)

    return vis[:l]

def cross(a, b): #checks if 2 lines cross/touch eachother
    return a[0] >= b[1] and a[0] <= b[2] and b[0] >= a[1] and b[0] <= a[2]

def toBW(p, sensitivity): #determines if pixel is black or white
    if p[0] + p[1] + p[2] > sensitivity:
         return 0
    return 1

def rect(x1, y1, x2, y2):
    x = (x1+x2)/2
    y = (y1+y2)/2
    w = x2-x1
    h = y2-y1
    return "StaticRect (%s, %s), (%s, %s), 0" % (x, y, w+8.2, h+8.2)

def getPic(URL):
    urlRead = urllib.urlopen(URL).read()
    picFile = cStringIO.StringIO(urlRead)
    return Image.open(picFile)

class FCMLImage:

    def __init__(self, imageurl, xtrans, ytrans, scale, sensitivity):
        self.imageurl = imageurl
        self.xtrans = xtrans
        self.ytrans = ytrans
        self.scale = scale
        self.sensitivity = sensitivity #the higher this is, the lower the sensitivity

    def partition(self):
        im = getPic(self.imageurl)
        (w, h) = im.size
        pixels = im.load()
        pix = [[0]*w for i in range(h)]
     
        for j in range(w):
            for i in range(h):
                pix[i][j] = toBW(pixels[j, i], self.sensitivity)
               
        vertices = []
        edges_x = []
        edges_y = []

        for i in range(h+1): #find and label vertices
            for j in range(w+1):
                s = 0
                if i > 0 and j > 0:
                    s += pix[i-1][j-1]
                if i > 0 and j < w:
                    s += pix[i-1][j]
                if i < h and j > 0:
                    s += pix[i][j-1]
                if i < h and j < w:
                    s += pix[i][j]

                if s == 2:
                    if i > 0 and j > 0 and i < h and j < w:
                        if pix[i][j] == pix[i-1][j-1]:
                            vertices.append((j, i, None, None)) #such a hack
                            vertices.append((j, i, None, None))

                if s == 1 or s == 3:
                    x = None
                    y = None
                    if s == 3:              
                        if pix[i][j] and pix[i-1][j]:
                            x = 'r'
                        else:
                            x = 'l'
                        if pix[i][j] and pix[i][j-1]:
                            y = 'd'
                        else:
                            y = 'u'
                    vertices.append((j, i, x, y))

        for i in range(0, len(vertices), 2): #get edges
            edges_x.append((vertices[i][1], vertices[i][0], vertices[i+1][0]))
        vertices.sort()    
        for i in range(0, len(vertices), 2):
            edges_y.append((vertices[i][0], vertices[i][1], vertices[i+1][1]))  

        lines = []
        vals = []

        for i in vertices: #get all "lines"
            if i[2] == 'r':            
                e = (w+1, 0, 0)
                for j in edges_y:
                    if j[0] > i[0] and j[0] < e[0] and j[1] <= i[1] and j[2] >= i[1]:
                        e = j              
                lines.append([(i[1], i[0], e[0])])

                if e[1] == i[1] or e[2] == i[1]:
                    vals.append([2])
                else:
                    vals.append([1])

            if i[2] == 'l':            
                e = (-1, 0, 0)
                for j in edges_y:
                    if j[0] < i[0] and j[0] > e[0] and j[1] <= i[1] and j[2] >= i[1]:
                        e = j              
                lines.append([(i[1], e[0], i[0])])

                if e[1] == i[1] or e[2] == i[1]:
                    vals.append([2])
                else:
                    vals.append([1])

            if i[3] == 'd':            
                e = (h+1, 0, 0)
                for j in edges_x:
                    if j[0] > i[1] and j[0] < e[0] and j[1] <= i[0] and j[2] >= i[0]:
                        e = j              
                lines[-1].append((i[0], i[1], e[0]))

                if e[1] == i[0] or e[2] == i[0]:
                    vals[-1].append(2)
                else:
                    vals[-1].append(1)

            if i[3] == 'u':            
                e = (-1, 0, 0)
                for j in edges_x:
                    if j[0] < i[1] and j[0] > e[0] and j[1] <= i[0] and j[2] >= i[0]:
                        e = j              
                lines[-1].append((i[0], e[0], i[1]))

                if e[1] == i[0] or e[2] == i[0]:
                    vals[-1].append(2)
                else:
                    vals[-1].append(1)

        graph = [[] for i in lines] #build graph
        for i in range(len(lines)):
            for j in range(len(lines)):
                if cross(lines[i][0], lines[j][1]):
                    graph[i].append(j)

        s = maxSet(graph, vals)
        lines_x = set()
        lines_y = set()
        for i in range(len(lines)):
            if s[i]:
                lines_x.add(lines[i][0])
            else:
                lines_y.add(lines[i][1])

        edges_x += list(lines_x)
        edges_y += list(lines_y)
        R = [] #result

        for i in edges_x:
            if i[0] >= h or pix[i[0]][i[1]] == 0:
                continue
            for j in edges_y:
                if j[1] == i[0] and j[0] < i[2] and j[0] >= i[1]: #find rectangle corner
                    minx = inf
                    miny = inf
                    for i2 in edges_x: #find bottom
                        if i2[0] > i[0] and i2[0] < minx and i2[1] <= j[0] and i2[2] > j[0]:
                            minx = i2[0]
                    for j2 in edges_y: #find side
                        if j2[0] > j[0] and j2[0] < miny and j2[1] <= i[0] and j2[2] > i[0]:
                            miny = j2[0]

                    R.append(rect(j[0]*10 - h*5, i[0]*10 - w*5, miny*10 - h*5, minx*10 - w*5))
        return "\n".join(map(str, R))

import urllib
import cStringIO
from PIL import Image

def getPic(URL):
    urlRead = urllib.urlopen(URL).read()
    picFile = cStringIO.StringIO(urlRead)
    return Image.open(picFile)

def getPixels(image):
    try:
        pixels = image.convert('RGB') # Feel free to use any format - manually convert it just in case...
        return pixels
    except Exception as e:
        print "Error in converting the image to pixels - check the image exists and is in a not-shitty format"
        print e

image = getPic("https://media2.giphy.com/media/MDXomrcGshGso/200_s.gif")
pixels = getPixels(image)
topLeftPixel = pixels.getpixel((0, 0))
print "R:" + str(topLeftPixel[0]) + " G:" + str(topLeftPixel[1]) + " B:" + str(topLeftPixel[2])

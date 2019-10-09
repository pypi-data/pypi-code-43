from PIL import Image, ImageFont, ImageDraw

class Justipy:
    def __init__(self,
                 image,
                 text,
                 tl_corner = [0, 0],
                 max_width = 400,
                 font="calibri.ttf",
                 fontsize=12,
                 line_space = 20,
                 fontcolor = (0,0,0),
                 paragraph_spaces = 0):
        self.status = True
        try:
            if(image.size[0]>0 and image.size[1]>0):
                self.im = image
        except:
            print("Invalid image.")
            self.status = False
        if(type(text) == str):
            self.text = text
        else:
            print("Invalid text.")
            self.status = False
        if(not (type(tl_corner) is list and len(tl_corner) == 2)):
            print("Wrong parameters set for the top left corner")
            self.status = False
        if(self.status and (tl_corner[0] > self.im.size[0] or tl_corner[1] > self.im.size[1])):
            print("The tl_corner point is out of the given image.")
            self.status = False
        if(self.status and (tl_corner[0] + max_width > self.im.size[0])):
            print("There is not enough horizontal space in the given image.")
            self.status = False
        if(max_width <= 10):
            print("The given maximum width is unreasonable.")
            self.status = False
        if(fontsize <= 4):
            print("The given font size is unreasonable.")
            self.status = False
        for color in fontcolor:
            if (not type(color) == int) or (color < 0) or (color > 255):
                print("Invalid color.")
                self.status = False
        if(not (type(paragraph_spaces) == int) or paragraph_spaces < 0):
            print("Number of spaces in the beginning of paragraph must be an integer greater or equal to zero.")
        if(self.status):
            self.tl_corner = tl_corner
            self.max_width = max_width
            self.fontsize = fontsize
            self.line_space = line_space
            self.fontcolor = fontcolor
            self.paragraph_spaces = paragraph_spaces
        if(line_space < fontsize):
            self.line_space = fontsize
        if(self.status):
            try:
                self.font = ImageFont.truetype(font, fontsize)
            except:
                print("The selected font is unavailable.")
                self.status = False
        if(self.status):
            self.paragraphs_txt = self.text.split("\n")
            self.paragraphs_lines = []
            self.getParagraphs()
            
    def getImage(self):
        return self.im

    def getStringSize(self, text):
        im = Image.new('RGB', (self.max_width, self.fontsize))
        draw = ImageDraw.Draw(im)
        x,_ = draw.textsize(text, font=self.font)
        return x

    def getLineBreaks(self, text):
        lts = text.split(" ")
        line = ""
        testline = ""
        out = []
        while(len(lts) > 0):
            for i in range(len(lts)):
                if(i == 0):
                    if(len(out) == 0):
                        line = " "*self.paragraph_spaces + lts[i]
                    elif(len(lts) == 1):
                        out.append(lts[0])
                        testline = ""
                        line = ""
                        del lts[0]
                        break
                    else:
                        line = lts[i]
                else:
                    testline = line + " " + lts[i]
                    if(self.getStringSize(testline) < self.max_width):
                        line = testline
                        if(i == len(lts) - 1):
                            out.append(line)
                            testline = ""
                            line = ""
                            del lts[0:i+1]
                            break
                    else:
                        out.append(line)
                        testline = ""
                        line = ""
                        del lts[0:i]
                        break
        return out
           
    def getParagraphs(self):
        for paragraph in self.paragraphs_txt:
           self.paragraphs_lines.append(self.getLineBreaks(paragraph))
        
    def drawJustifiedText(self):
        if(self.status):
            draw = ImageDraw.Draw(self.im)
            x_mem = self.tl_corner[0]
            y_mem = self.tl_corner[1]
            x = self.tl_corner[0]
            y = self.tl_corner[1]
            for paragraph in self.paragraphs_lines:
                for i in range(len(paragraph)):
                    free_space = 0
                    if(i == 0 and len(paragraph) > 0):
                        free_space = self.max_width - self.getStringSize(" "*self.paragraph_spaces + paragraph[i].replace(" ",""))
                    else:
                        free_space = self.max_width - self.getStringSize(paragraph[i].replace(" ",""))
                    words = paragraph[i].replace(" "*self.paragraph_spaces, "").split(" ")
                    number_of_spaces = len(words) - 1
                    size_of_spaces = int(free_space / number_of_spaces) if number_of_spaces != 0 else 0
                    if(i == len(paragraph) - 1):
                        size_of_spaces = self.getStringSize(" ")
                    for j in range(len(words)):
                        if(i == 0 and j == 0):
                            draw.text((x_mem, y_mem), " "*self.paragraph_spaces+words[j], self.fontcolor, font=self.font)
                            x_mem += self.getStringSize(" "*self.paragraph_spaces+words[j]) + size_of_spaces
                        elif(j == len(words) - 1 and i != len(paragraph) - 1):
                            draw.text((x+self.max_width-self.getStringSize(words[j]), y_mem), words[j], self.fontcolor, font=self.font)
                        else:
                            draw.text((x_mem, y_mem), words[j], self.fontcolor, font=self.font)
                            x_mem += self.getStringSize(words[j]) + size_of_spaces
                    x_mem = x
                    y_mem += self.line_space

    def drawCentralizedText(self):
        if(self.status):
            draw = ImageDraw.Draw(self.im)
            x_mem = self.tl_corner[0]
            y_mem = self.tl_corner[1]
            for paragraph in self.paragraphs_lines:
                for line in paragraph:
                    l_pad = int((self.max_width - self.getStringSize(line))/2)
                    draw.text((x_mem+l_pad, y_mem), line, self.fontcolor, font=self.font)
                    y_mem += self.line_space
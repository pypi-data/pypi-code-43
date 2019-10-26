from pihat_widget import image


class LEDCharacter(image.ImageLoader):

    def __init__(self,x,y):
        super().__init__(origin_x=x, origin_y=y, origin_width=45, origin_height=77, offsetx=0, offsety=0)
        self.__number = None

    @property
    def Number(self):
        return self.__number
    @Number.setter
    def Number(self, number):
        if type(number) is int:
            self.q.put(("load",str(number)))
            self.__number = number
        else:
            raise ValueError("Number must be an int")


class LEDMultiCharacter:

    def __del__(self):
        self.close()

    def __init__(self, digits):

        self.__digits = digits
        self.__chars = [LEDCharacter(10+(i*45),10) for i in range(digits)]
        self.__number = None
        for z in self.__chars:
            z.Number =0

    @property
    def Number(self):
        return self.__number

    @Number.setter
    def Number(self, number):
        if type(number) is int:

            num = f"{number:0{self.__digits}d}"
            for c,n in enumerate(num):
                self.__chars[c].Number = int(n)

        else:
            raise ValueError("Number must be an int")
    def close(self):
        for c in self.__chars:
            c.close()

if __name__ == "__main__":


    c = LEDMultiCharacter(5)
    for i in range(105):
        c.Number =i
    c.close()


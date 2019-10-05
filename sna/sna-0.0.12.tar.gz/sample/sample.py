from sna.search import Sna

sna = Sna()
# sna.default = sna.regex
# sna.default = sna.literal
# sna.default = sna.filter(lambda x: x > 50 )


@sna("(.*d.*r.*)")
def wow(ctx):
    print(ctx.match.groups(0))


@sna("(.*d.*r.*)")
class DR_word(object):
    def __init__(self, match):
        self.content = match.group(1)

    def read(self):
        print(self.content)


@sna("(.*e.*t.*)")
class ET_word(object):
    def __init__(self, match):
        self.content = match.group(1)

    def read(self):
        print(self.content)


# if you prefer functions way
sna.search("wow").through.lines().on(
    stg="dadasdfrsfdr veli eadsft"
).run()

print(80 * "-")

# find all patterns
# which has read method
# functions only has run method
sna.search().through.words().on(
    filepath="inputs/sample.txt"
).read()

print(80 * "-")

# Or be specific
sna.search("ET_word").through.words().on(
    filepath="inputs/sample.txt"
).read()


import objutils as ob

FL = r"F:\projekte\csProjects\XCP\cXCP\XCP_SIM\XCPSIM_Flash.rom"

b0 = ob.section.Section(0x10, "\x11" * 0x10)
b1 = ob.section.Section(0x50, "\x22" * 0x10)

img = ob.image.Image([b0, b1])

d = ob.loads('bin', bytes([1,2,3,4]), address=0x8600)
print(d)

print(d.hexdump())
#print(ob.dumps('srec', d))
d1 = ob.load("bin", open(FL, "rb"), address = 0x8000)
print(d1)
d1.hexdump()

print(b0)
print(b1)
print(img)
print(img.hexdump())
print(ob.dump("bin", open("test01.bin", "wb"), img))
print(ob.dumps("binzip", img))

d2 = ob.load("bin", open("test01.bin", "rb"), address = 0x8010)
print(d2)
d2.hexdump()


from arlulaapi import ArlulaSession

key = "zWJoNGMcF9utRJN41520yXrBVWKxqQEaKEwrkyj_pcaLQi3Nj56-Z-taopFx2TZbFycGStEDs4CsQxIB"
secret = "SHEDiNEateREsTroParzabLevOcowdRaPhOmpedu"
session = ArlulaSession(key, secret)
res = session.search(start="2014-01-01",res="vlow",lat=40.84,long=60.15)
res = session.order(id="MF69PaGWzMOQM5nPOR3AG7Jz24xRfUMLnfxu2B2XhMC+/92X0KPMSZ2rSipQdPXyoUzf5N3JompaOSwAro9+qhfIw28J+owxWKkMLHsgQgiB4q/UKEZmDsRGnGRBSar3eiKrUdk",
                    eula="",
                    seats=1,
                    webhooks=[],
                    emails=["adamhammo99@gmail.com"])
session.get_resource(id="06e11187-9461-4ae2-9987-8ac9dd50e9c5",
                     filepath="test.jpg")
session.get_order_resources(id="06e11187-9461-4ae2-9987-8ac9dd50e9c5", folder="./test")
# s = [
#         {
#             "start":"2014-01-01",
#             "res":"vlow",
#             "lat":40.84,
#             "long":60.15
#         },
#         {
#             "start":"2014-01-01",
#             "end":"2014-02-01",
#             "res":"vlow",
#             "lat":30,
#             "long":30   
#         }
#     ]
# r = session.gsearch(s)
# print(r)
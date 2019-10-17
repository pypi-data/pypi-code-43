# -*- coding: utf-8 -*-
from nfe.utils.rsa import Rsa


privateKeyContent = open("../static/rsaKey.pem").read()

text = b"abcabc"
text2 = b"ábçabc"

digest = Rsa.digest(text=text2)
# signature = Rsa.sign(text=text2, privateKeyContent=privateKeyContent)

print(digest)

#Digest2.7: 0xfPq074N3UvYzNOHb963OTLqNo=

#Digest3.7: 0xfPq074N3UvYzNOHb963OTLqNo=
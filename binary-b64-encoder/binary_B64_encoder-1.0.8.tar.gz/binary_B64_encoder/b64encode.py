import codecs
import binascii
import argparse

def byteParser(byte):
    torun = True
    res = ""
    while torun:
        try:
            byte = byte[0:len(byte)-1]
            res = binascii.a2b_base64(codecs.decode(byte+"=","base64"))
            torun = False
        except:
            pass
    return res

def decode(filepath):
    byte = "1"
    in_file = open(filepath,"rb")
    output_fname = "{file}.decoded".format(
        file=filepath
    )
    out_file = open(
       output_fname ,"wb"
    )
    count = 0 
    while byte != "":
        try:
            byte = in_file.read(244)
            #print byte
            if byte[0:10] == "__INICIO__": 
                byte = byte.replace("__INICIO__","")
                out_file.write(
                    binascii.a2b_base64(
                        codecs.decode(byte+"=","base64")
                    )
                )
            else:
                bytes = byte.split("__INICIO__")
                for b in bytes:
                    out_file.write(
                        binascii.a2b_base64(
                            codecs.decode(b+"==","base64")
                        )
                    )
        except:
            out_file.write(byteParser(byte))
    in_file.close()
    out_file.close()
    print(output_fname)

def encode(filepath):
    byte = "1"
    output_fname = "{file}.b64".format(
            file=filepath
        )
    in_file = open(filepath,"rb")
    out_file = open(output_fname,"wb")
    while byte != "":
        byte = in_file.read(128)
        encode = codecs.encode(binascii.b2a_base64(byte),"base64")
        #out_file.write("__INICIO__" + encode[0:(len(encode)-2)] + "__FIN__")
        out_file.write("__INICIO__" + encode[0:(len(encode)-2)] )
    in_file.close()
    out_file.close()
    print(output_fname)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--encode",help="FILE PATH",required=False)
    parser.add_argument("--decode",help="FILE PATH",required=False)
    args = parser.parse_args()
    if args.decode==None and args.encode==None:
        args = parser.parse_args(["-h"])
        exit()
    if args.decode!=None:
        decode(args.decode)
        exit()
    if args.encode!=None:
        encode(args.encode)
    

if __name__=="__main__":
    main()
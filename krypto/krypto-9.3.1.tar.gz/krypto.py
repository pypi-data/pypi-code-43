import time
import os
import sys
import base64
from os import system, name
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
import webbrowser
import getpass
import random
from PIL import Image
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from itertools import zip_longest as zip
from licensing.models import *
from licensing.methods import Key, Helpers
import datetime


def main():
    try:
        def encrypt(key, filename):
            chunksize = 4096 * 65536
            outputFile = filename + ".encrypted"
            filesize = str(os.path.getsize(filename)).zfill(65536)  # 32768
            IV = Random.new().read(16)

            encryptor = AES.new(key, AES.MODE_CBC, IV)

            with open(filename, 'rb') as infile:
                with open(outputFile, 'wb') as outfile:
                    outfile.write(filesize.encode('utf-8'))
                    outfile.write(IV)

                    while True:
                        chunk = infile.read(chunksize)

                        if len(chunk) == 0:
                            break
                        elif len(chunk) % 65536 != 0:
                            chunk += b' ' * (65536 - (len(chunk) % 65536))

                        outfile.write(encryptor.encrypt(chunk))

        def decrypt(key, filename):
            chunksize = 4096 * 65536
            outputFile = filename[:9]

            with open(filename, 'rb') as infile:
                filesize = int(infile.read(65536))
                IV = infile.read(16)

                decryptor = AES.new(key, AES.MODE_CBC, IV)

                with open(outputFile, 'wb') as outfile:
                    while True:
                        chunk = infile.read(chunksize)

                        if len(chunk) == 0:
                            break

                        outfile.write(decryptor.decrypt(chunk))
                    outfile.truncate(filesize)

        def getKey(password):
            hasher = SHA256.new(password.encode('utf-8'))
            return hasher.digest()

        def clear():
            return os.system('cls')

        clear()

        if os.path.isfile("./enctxt.dll"):
            enc_txt = open("enctxt.dll", "r", encoding="utf8")
            if enc_txt.mode == "r":
                enc_txt_contents = enc_txt.read()
                print(enc_txt_contents)
            else:
                print(" ")
        else:
            print(" ")

        print(''' Encryptor [Version 9.3.1] by krish
 Type 'help' to view all commands''')
        license_key = LicenseKey.load_from_string(pubKey, f.read())
        print(" License expires: " + str(license_key.expires))
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(" ")

        def encryption():
            try:
                filename = input(" File to encrypt (with extension): ")
                time.sleep(1)
                password = input(" Password: ")
                time.sleep(2)
                encrypt(getKey(password), filename)
                print(" Your file has been encrypted.\n")
                time.sleep(1)

            except FileNotFoundError:
                print("\n Error: File not found!")

        def decryption():
            try:
                filename = input(" File to decrypt (with FULL extension): ")
                time.sleep(1)
                password = input(" Password: ")
                time.sleep(2)
                decrypt(getKey(password), filename)
                print(" Your file has been decrypted.\n")
                time.sleep(1)

            except FileNotFoundError:
                print("\n Error: File not found!")

        def img_main_encrypt():
            try:

                def Set_LSB(value, bit):
                    if bit == '0':
                        value = value & 254
                    else:
                        value = value | 1
                    return value

                def Hide_message(carrier, message, outfile):
                    message += chr(0)
                    c_image = Image.open(carrier)
                    c_image = c_image.convert('RGBA')

                    out = Image.new(c_image.mode, c_image.size)
                    pixel_list = list(c_image.getdata())
                    new_array = []

                    for i in range(len(message)):
                        char_int = ord(message[i])
                        cb = str(bin(char_int))[2:].zfill(8)
                        pix1 = pixel_list[i * 2]
                        pix2 = pixel_list[(i * 2) + 1]
                        newpix1 = []
                        newpix2 = []

                        for j in range(0, 4):
                            newpix1.append(Set_LSB(pix1[j], cb[j]))
                            newpix2.append(Set_LSB(pix2[j], cb[j + 4]))

                        new_array.append(tuple(newpix1))
                        new_array.append(tuple(newpix2))

                    new_array.extend(pixel_list[len(message) * 2:])

                    out.putdata(new_array)
                    out.save(outfile)
                    print(" Steg image saved to " + outfile + "\n")

                input_image = input(
                    "\n Enter the name of the image (with extension): ")

                input_message = input(" Enter the data to be encoded: ")

                output_image = input(
                    " Enter the name of the new image (without extension): ")

                output_image_ext = output_image + ".png"

                Hide_message(input_image, input_message, output_image_ext)

            except FileNotFoundError:
                time.sleep(1)
                print("\n Error: Image file not found!")
            except AttributeError:
                time.sleep(1)
                print("\n Error: File not found!")
            except ValueError:
                time.sleep(1)
                print("\n Error: Please enter a value!")

        def img_main_decrypt():

            try:
                def get_pixel_pairs(iterable):
                    a = iter(iterable)
                    return zip(a, a)

                def get_LSB(value):
                    if value & 1 == 0:
                        return '0'
                    else:
                        return '1'

                def extract_message(carrier):
                    c_image = Image.open(carrier)
                    pixel_list = list(c_image.getdata())
                    message = ""

                    for pix1, pix2 in get_pixel_pairs(pixel_list):
                        message_byte = "0b"
                        for p in pix1:
                            message_byte += get_LSB(p)

                        for p in pix2:
                            message_byte += get_LSB(p)

                        if message_byte == "0b00000000":
                            break

                        message += chr(int(message_byte, 2))
                    return message

                steg_input = input(" Enter image name (with extension): ")

                print(" " + extract_message(steg_input) + "\n")

            except FileNotFoundError:
                time.sleep(1)
                print("\n Error: Image file not found!")
            except AttributeError:
                time.sleep(1)
                print("\n Error: File not found!")
            except ValueError:
                time.sleep(1)
                print("\n Error: Please enter a value!")

        while True:
            path = os.getcwd()

            encInput = input(" encryptor@root:" + path + "~$ ")

            if encInput == "help":
                time.sleep(0.5)
                print(
                    ''' encrypt          encrypt any file with AES256 encryption
 decrypt          decrypt any file encrypted by the "encrypt" command

 txt_encrypt      encrypt any text or data
 txt_decrypt      decrypt text or data encrypted with the "txt_encrypt" command

 img_encrypt      hide data in images (Supported files - PNG, JPEG, GIF, TIFF)
 img_decrypt      decrypt data encrypted by the "img_encrypt" command

 sshkeygen        generate a SSH key pair
 gen_passwd       generate a secure random password
 ls               list all the files in a folder
 cd..             move out of a folder
 cd               move inside a folder
 mkdir            create a new directory
 clear            clear the screen
 exit             exit the Encryptor\n''')

            elif encInput == "encrypt":
                encryption()

            elif encInput == "decrypt":
                decryption()

            elif encInput == "mkdir":
                dir_name = input(" Name of directory: ")
                time.sleep(1)

                if dir_name == "" or dir_name == " ":
                    print(" \n Error: Enter a valid name!")

                else:

                    def createFolder(directory):
                        try:
                            if not os.path.exists(directory):
                                os.makedirs(directory)

                        except OSError:
                            print(' Error: Creating directory. ' + directory)

                    createFolder("./" + dir_name + '/')
                    print(" Directory created.\n")
                    time.sleep(0.3)

            elif encInput == "img_encrypt":
                img_main_encrypt()

            elif encInput == "img_decrypt":
                img_main_decrypt()

            elif encInput == "ls":
                path = '.'
                files = os.listdir(path)
                for name in files:
                    print(" " + name)

            elif encInput == "exit":
                print("\n\n Exiting....")
                time.sleep(3)
                sys.exit()

            elif encInput == "clear":
                print("\n")
                os.system('cls')

            elif encInput == "":
                print(" ")

            elif encInput == " ":
                print(" ")

            elif encInput == "  ":
                print(" ")

            elif encInput == "   ":
                print(" ")

            elif encInput == "cd..":
                os.chdir("..")
                print(" ")

            elif encInput == "cd":
                directory = input(r" Dir: ")
                os.chdir(directory)
                print(" ")

            elif encInput == "gen_passwd":

                try:
                    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@£$%^&*.,?0123456789"
                    time.sleep(0.5)
                    number = input(' \n Number of passwords: ')
                    number = int(number)

                    length = input(' Password length: ')
                    length = int(length)

                    print('\n Here are your passwords: ')

                    for pwd in range(number):
                        password = ''
                        for c in range(length):
                            password += random.choice(chars)
                        print(" " + password + "\n")
                except ValueError:
                    print("\n Error: Please enter a value!")

            elif encInput == "sshkeygen":

                # generate private/public key pair
                key = rsa.generate_private_key(
                    backend=default_backend(),
                    public_exponent=65537,
                    key_size=2048)

                # get public key in OpenSSH format
                public_key = key.public_key().public_bytes(
                    serialization.Encoding.OpenSSH,
                    serialization.PublicFormat.OpenSSH)

                # get private key in PEM container format
                pem = key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption())

                # decode to printable strings
                private_key_str = pem.decode('utf-8')
                public_key_str = public_key.decode('utf-8')

                print(' Private Key: ')
                print(" " + private_key_str)
                print(' Public Key: ')
                print(" " + public_key_str)
                print(" ")

            elif encInput == "txt_encrypt":
                def txt_encrypt(plaintext, password):
                    f = Fernet(
                        base64.urlsafe_b64encode(
                            PBKDF2HMAC(
                                algorithm=hashes.SHA256(),
                                length=32,
                                salt=b'abcd',
                                iterations=1000,
                                backend=default_backend()).derive(
                                password.encode())))
                    return f.encrypt(plaintext.encode()).decode()


                password = "!J$4FukvFDk*v%p2_tnVGqjwE_*cNwpJdnH9ccGFH%rGq=nQyS6SRUYz?LzB^%*Ke36knj9=^5wk-gX-_%svw#a+5wpxE*N&YR7$C9Pv!JE-4zdP!$twcHBcV6bNCNFsEaBBkbSsDFXXFedSN#A^P4jVr!veJ@RQ5_qv=2#suBpyEc7pNGs=H6?XC5MAvCm%=6Gj&Y*YTaTRAAVQqb9SZ$x=Qj7b6CZ?wR*zgHjH%gjwUDK!KnnvnWs^Hq^-ByumYCcnkB3WEHDUmW4_xasxfVdveW6hGeGM3Wcsxv+=#?SBcp8mfhW7qdqu!9Ebx^UZ2w@cNVSc9@E*@+D9^Y+4yn5hMUxt&hJFVQwV%UF9XFswn4Bcp3Q5VxzS2F?&E?J92a55#U!9NxHUZNW-5cuRtAfBXYRFrfZ$HDUa=5=VUxT%3_2g?eVh7_LD@eTTW^4e8U8B+p!L_2WrJ$?+=MGC*x9zxdN6BCY5rEbYsjqm&yRc=-^sF$SKFaS^ZLR*w4QaFwhk2NLSyBCdbdeAga5RB8_C^Nzxc@BSa_j$m!j-$vUdqQ#pd648qWMQ*H$bFWmVs74P#_k38H6G%u4KMx?dy_^7CWg^Wumh@KZFak$3N^RnN+yJ2d_gP#k?@mxjJZq%uWr-FhKNEyCE22MQdsRjjH!HqHjX3Aa#k?4R4@XxRd#Q2B%!qSCG4DUc6D9TpHesWwrDh#28DEV@4__2^&r!wRFTppDJdYXaW2rQGWC!C9$NwZ95K98nU8YD_LX-#996Kv%fd%W7%M7r7MbbArmDaNprkD%cM=hSgnh!$uCpJvSa%PA*mM2M+xc^#5-B$N*Dhhy*yZqbW3LZbs8U!WQ%5kt7+yCr^x3$PK3e*EyjeCNXV+ZTSW=#@e_WV^5k#w+PtwYCFE98N_Un&%YPE=+?g#t-Xxx?sZ3FVjzUCWYxSC9m4EJ9MVfX$A89hpfJ-ahMc=MLnE32D+DV7%=N8EfUuu9?^7_9ZaQvrv=%yPDx#*XqTpSApV#ByUc%kd=?ugZ4"

            
                def txt_encryption():
                    try:
                        enc_data = input(" Enter data to encode: ")
                        encrypted = txt_encrypt(enc_data, password)
                        time.sleep(1)
                        print("\n Encrypted data: ")
                        print(" " + encrypted)
                        print(" ")
                    except BaseException:
                        time.sleep(1)
                        print("\n Error: Encrypted text is invalid!")

                txt_encryption()

                

                

            elif encInput == "txt_decrypt":
                def txt_decrypt(ciphertext, password):
                    f = Fernet(
                        base64.urlsafe_b64encode(
                            PBKDF2HMAC(
                                algorithm=hashes.SHA256(),
                                length=32,
                                salt=b'abcd',
                                iterations=1000,
                                backend=default_backend()).derive(
                                password.encode())))
                    return f.decrypt(ciphertext.encode()).decode()

                password = "!J$4FukvFDk*v%p2_tnVGqjwE_*cNwpJdnH9ccGFH%rGq=nQyS6SRUYz?LzB^%*Ke36knj9=^5wk-gX-_%svw#a+5wpxE*N&YR7$C9Pv!JE-4zdP!$twcHBcV6bNCNFsEaBBkbSsDFXXFedSN#A^P4jVr!veJ@RQ5_qv=2#suBpyEc7pNGs=H6?XC5MAvCm%=6Gj&Y*YTaTRAAVQqb9SZ$x=Qj7b6CZ?wR*zgHjH%gjwUDK!KnnvnWs^Hq^-ByumYCcnkB3WEHDUmW4_xasxfVdveW6hGeGM3Wcsxv+=#?SBcp8mfhW7qdqu!9Ebx^UZ2w@cNVSc9@E*@+D9^Y+4yn5hMUxt&hJFVQwV%UF9XFswn4Bcp3Q5VxzS2F?&E?J92a55#U!9NxHUZNW-5cuRtAfBXYRFrfZ$HDUa=5=VUxT%3_2g?eVh7_LD@eTTW^4e8U8B+p!L_2WrJ$?+=MGC*x9zxdN6BCY5rEbYsjqm&yRc=-^sF$SKFaS^ZLR*w4QaFwhk2NLSyBCdbdeAga5RB8_C^Nzxc@BSa_j$m!j-$vUdqQ#pd648qWMQ*H$bFWmVs74P#_k38H6G%u4KMx?dy_^7CWg^Wumh@KZFak$3N^RnN+yJ2d_gP#k?@mxjJZq%uWr-FhKNEyCE22MQdsRjjH!HqHjX3Aa#k?4R4@XxRd#Q2B%!qSCG4DUc6D9TpHesWwrDh#28DEV@4__2^&r!wRFTppDJdYXaW2rQGWC!C9$NwZ95K98nU8YD_LX-#996Kv%fd%W7%M7r7MbbArmDaNprkD%cM=hSgnh!$uCpJvSa%PA*mM2M+xc^#5-B$N*Dhhy*yZqbW3LZbs8U!WQ%5kt7+yCr^x3$PK3e*EyjeCNXV+ZTSW=#@e_WV^5k#w+PtwYCFE98N_Un&%YPE=+?g#t-Xxx?sZ3FVjzUCWYxSC9m4EJ9MVfX$A89hpfJ-ahMc=MLnE32D+DV7%=N8EfUuu9?^7_9ZaQvrv=%yPDx#*XqTpSApV#ByUc%kd=?ugZ4"


                def txt_decryption():
                    try:
                        dec_data = input(" Enter data to decode: ")
                        dec_len = len(dec_data)
                        #if dec_len > 100:
                         #   time.sleep(1)
                          #  print("\n Error: Invalid data!")
                        #elif dec_len < 100:
                         #   time.sleep(1)
                          #  print("\n Error: Invalid data!")
                        #else:
                        decrypted = txt_decrypt(dec_data, password)
                        time.sleep(1.5)
                        print("\n Decrypted data: ")
                        print(" " + decrypted)
                        print(" ")

                    except BaseException:
                        time.sleep(1)
                        print("\n Error: Encrypted text is invalid!")

                txt_decryption()



            else:
                print(
                    "\n"
                    " '" +
                    encInput +
                    "'" +
                    " is not recognized as a command")

    except KeyboardInterrupt:
        print("\n\n\n Exiting....")
        time.sleep(2)
        sys.exit()


try:

    def f_clear():
        return os.system('cls')
    f_clear()

    if os.path.isfile("./enctxt.dll"):
        enc_txt = open("enctxt.dll", "r", encoding="utf8")
        if enc_txt.mode == "r":
            enc_txt_contents = enc_txt.read()
            print(enc_txt_contents)
        else:
            print(" ")
    else:
        print(" ")

    print(" Encryptor [Version 9.3.1] by krish")

    if os.path.isfile('./license.skm'):
        try:
            pubKey = "<RSAKeyValue><Modulus>yL/FijjXjxh9yHJ3hz/2ADy+QQbEcqY7HdFRY+n5zZVO7uRl2eUphLGB5sI55Tp8/T/D12geupNZ+L8SVtNwl7saVszsOiWrOvybo3zx13VXtb3ByIo6oN68A5rdpQkAVKVy7MfMGz44xs8RuTnogWI+NYAEOnSR3K/Q+rg7kQsIn2dbnmQq6AwLTSWeSABWgT6kITztxK5OHzJng14GWecsq9mO6w1gZnl40uKHjGZ+mKIAiie32BD8BZby9YWkXmeg3x2/HRQuFKHvSX36BlaDa7DnUsJVB27S9RB1VfxluyhtULE5dK3umfnHht5fAiUIphMADTjl3RU2Ahwftw==</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>"
            # read license file from file
            with open('license.skm', 'r') as f:
                license_key = LicenseKey.load_from_string(pubKey, f.read())
                
                time.sleep(2)
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                expdate = license_key.expires
                nowdate = datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                if nowdate >= expdate:
                    time.sleep(1.5)
                    print(" \n Error: License has expired!")
                    time.sleep(1.5)
                    print("\n\n Exiting...")
                    time.sleep(3)
                    sys.exit()
                #now_enc = base64.b64encode(now)
                #now_file = open("tdate.encryptor", "w+")
                #now_file.write(now_enc)
                #now_file.close()
                else:
                    if __name__ == "__main__":
                        main()

        except AttributeError:
            print("\n Error: Invalid License!")
            time.sleep(2)
            sN=getpass.getpass(prompt="\n\n Press the 'Enter' key to exit. ")

    else:

        key_input = input(" \n Please enter the license key: ")

        pubKey = "<RSAKeyValue><Modulus>yL/FijjXjxh9yHJ3hz/2ADy+QQbEcqY7HdFRY+n5zZVO7uRl2eUphLGB5sI55Tp8/T/D12geupNZ+L8SVtNwl7saVszsOiWrOvybo3zx13VXtb3ByIo6oN68A5rdpQkAVKVy7MfMGz44xs8RuTnogWI+NYAEOnSR3K/Q+rg7kQsIn2dbnmQq6AwLTSWeSABWgT6kITztxK5OHzJng14GWecsq9mO6w1gZnl40uKHjGZ+mKIAiie32BD8BZby9YWkXmeg3x2/HRQuFKHvSX36BlaDa7DnUsJVB27S9RB1VfxluyhtULE5dK3umfnHht5fAiUIphMADTjl3RU2Ahwftw==</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>"

        res = Key.activate(
            token="WyI4NDMxIiwid0lRVTlVOXhhNTloZHpPUHpsM2dvQ0x3NHBCeWtKTW1mSFp4L005cyJd",
            rsa_pub_key=pubKey,
            product_id=4970,
            key=key_input,
            machine_code=Helpers.GetMachineCode())

        if res[0] is None or not Helpers.IsOnRightMachine(res[0]):
            print(" An error occurred: {0}".format(res[1]))
            time.sleep(3)
        else:
            print("\n Activated! \n")
            time.sleep(3)

            # res is obtained from the code above
            if res[0] is not None:
                # saving license file to disk
                with open("license.skm", "w") as f:
                    f.write(res[0].save_as_string())

            license_key = res[0]
            # print("Feature 1: " + str(license_key.f1))
            if __name__ == "__main__":
                main()

except KeyboardInterrupt:
    print("\n\n\n Exiting....")
    time.sleep(2)
    sys.exit()
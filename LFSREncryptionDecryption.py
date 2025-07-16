#LFSR Encryption by Benjamin Vartanian

initialValue= 0x5876423
#Set data to whatever you want encrypted by the LFSR algorithm
data = "this is stored as plaintext"
dataAsBytes = bytes(data, encoding="ascii")

#Method to make a byte array print out in a correct format
def makePretty(byteArray):
    prettyString = ""
    for x in byteArray:
        #Formatting logic to add the hex indicator before each byte, as well as limiting it
        #to only the last 2 digits and force it to display both digits instead of shortening
        #(\x01 was becoming \x1)
        prettyString += f'\\x{x:02X}'
    return prettyString


def LFSREncrypt(data: bytes, initialValue: int) -> bytes:
    result = bytearray()
    state=initialValue
    feedback=0x9999999 # aka the encryption key, Never changes
    for byte in data:
        #simple method will run the logic on stepping based on the lowest bit 8 times for us
        #and return the byte after it's gone through that logic
        state=simple(state, feedback)
        # Adding an and with a maxed binary number lets us see whether or not the
        # 1s position will roll over to zero or not
        lowestbyte=(state & 0b11111111)
        # xor
        lowestbyte= byte ^ lowestbyte
        #add each encrypted byte to a byte array (result)
        result.append(lowestbyte)
    return bytes(result)

#simple runs the logic of the LFSR algorithm, where it checks if the smallest bit is 0 or 1 using mod 2
#before performing the relevant operation on the passed in byte
def simple(s: int, f: int) -> int:
    #The number of steps it shifts can be changed in range(), but 8 was what was specified
    for x in range(8):
        if(s % 2 == 0):
            s >>= 1
        elif(s % 2 == 1):
            s = (s>>1) ^ f
    return(s)

#a few tests to make sure the code is working, first one is for simple
#test1=simple(0xFFFFFFFF, 0x87654321)
#if test1!=0x9243f425:
#    print(f"simple didn't work {test1=}")
#else:
#    print("simple OK")

#test1=test1 & 0b11111111

#if test1  != 0x25:
#    print(f"simple didn't work {test1=}")

#if 0x41 ^ test1 != 0x64:
#    print(f"simple didn't work {test1=}")

encrypted=LFSREncrypt(dataAsBytes, initialValue)
decrypted = LFSREncrypt(encrypted, initialValue)
#makePretty just makes it look better when encrypting
print("Your data encrypted appears as: ")
print(makePretty(encrypted) + "\n")
print("And applying that encrypted data through the same algorithm decrypts it: ")
print(decrypted)

class PaddingError(Exception):
    pass

MAXLINESIZE = 76 # Excludes the Carriage Return Line Feed
MAXFILESIZE = (MAXLINESIZE//4)*3


#Decode base64-encoded ASCII characters back into the original text.

table_a2b_base64 = { #Base64 ASCII to Binary Dictionary
    'A': 0,
    'B': 1,
    'C': 2,
    'D': 3,
    'E': 4,
    'F': 5,
    'G': 6,
    'H': 7,
    'I': 8,
    'J': 9,
    'K': 10,
    'L': 11,
    'M': 12,
    'N': 13,
    'O': 14,
    'P': 15,
    'Q': 16,
    'R': 17,
    'S': 18,
    'T': 19,
    'U': 20,
    'V': 21,
    'W': 22,
    'X': 23,
    'Y': 24,
    'Z': 25,
    'a': 26,
    'b': 27,
    'c': 28,
    'd': 29,
    'e': 30,
    'f': 31,
    'g': 32,
    'h': 33,
    'i': 34,
    'j': 35,
    'k': 36,
    'l': 37,
    'm': 38,
    'n': 39,
    'o': 40,
    'p': 41,
    'q': 42,
    'r': 43,
    's': 44,
    't': 45,
    'u': 46,
    'v': 47,
    'w': 48,
    'x': 49,
    'y': 50,
    'z': 51,
    '0': 52,
    '1': 53,
    '2': 54,
    '3': 55,
    '4': 56,
    '5': 57,
    '6': 58,
    '7': 59,
    '8': 60,
    '9': 61,
    '+': 62,
    '/': 63,
    '=': 0,
}

def a2b_base64(k):
    if not isinstance(k, (str, unicode)):
        raise TypeError("expected a string or unicode, received instead %r" % (k,))
    k = k.rstrip()
    # removes invalid characters, strips the final '=' padding
    # and checks for correct padding

    def next_valid_char(k, pos):
        for i in range(pos + 1, len(k)):
            char = k[i]
            if char < '\x7f':
                try:
                    table_a2b_base64[char]
                    return char
                except KeyError:
                    pass
        return None

    quad_pos = 0
    lbits = 0
    lchar = 0
    res = []
    for i, char in enumerate(k):
        if char == '\n' or char == '\r' or char > '\x7f' or char == ' ':
            continue
        if char == '=':
            if (quad_pos == 2 and next_valid_char(char, i) != '=') or quad_pos < 2:
                continue
            else:
                lbits = 0
                break
        try:
            next_char = table_a2b_base64[char]
        except KeyError:
            continue
        quad_pos = (quad_pos + 1) & 0x03
        lchar = (lchar << 6) | next_char
        lbits += 6
        if lbits >= 8:
            lbits -= 8
            res.append((lchar >> lbits & 0xff))
            lchar &= ((1 << lbits) - 1)
    if lbits != 0:
        raise PaddingError('Incorrect file padding')
    
    return ''.join([chr(i) for i in res])

def decode(input, output):
    while True:
        line = input.readline()
        if not line:
            break
        k = a2b_base64(line)
        output.write(k)


#Encode any plain-text file into a string of ASCII characters using base64.

table_b2a_base64 = \
"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

def b2a_base64(k):
    length = len(k)
    final_length = length % 3

    def triples_gen(k):
        while k:
            try:
                yield ord(k[0]), ord(k[1]), ord(k[2])
            except IndexError:
                k += '\0\0'
                yield ord(k[0]), ord(k[1]), ord(k[2])
                return
            k = k[3:]

    a = triples_gen(k[ :length - final_length])

    result = [''.join(
        [table_b2a_base64[( A >> 2                    ) & 0x3F],
         table_b2a_base64[((A << 4) | ((B >> 4) & 0xF)) & 0x3F],
         table_b2a_base64[((B << 2) | ((C >> 6) & 0x3)) & 0x3F],
         table_b2a_base64[( C                         ) & 0x3F]])
              for A, B, C in a]

    final = k[length - final_length:]
    if final_length == 0:
        piece = ''
    elif final_length == 1:
        a = ord(final[0])
        piece = table_b2a_base64[(a >> 2 ) & 0x3F] + \
                  table_b2a_base64[(a << 4 ) & 0x3F] + '=='
    else:
        a = ord(final[0])
        b = ord(final[1])
        piece = table_b2a_base64[(a >> 2) & 0x3F] + \
                  table_b2a_base64[((a << 4) | (b >> 4) & 0xF) & 0x3F] + \
                  table_b2a_base64[(b << 2) & 0x3F] + '='
    return ''.join(result) + piece + '\n'

def encode(input, output):
    while True:
        k = input.read(MAXFILESIZE)
        if not k:
            break
        while len(k) < MAXFILESIZE:
            nk = input.read(MAXFILESIZE-len(k))
            if not nk:
                break
            k += nk
        line = b2a_base64(k)
        output.write(line)


#Usage Example

with open('C:\Project Info.txt', 'rb') as input, open('C:\Project Info.encoded.txt', 'w') as output:
    encode(input, output) #Be sure to include the file location and appropriate extension with the input and output arguments (as shown).

with open('C:\Project Info.encoded.txt', 'rb') as input, open('C:\Project Info.txt.decoded.txt', 'w') as output:
    decode(input, output) #It is important to name the output file using the original file extension, txt in this example.

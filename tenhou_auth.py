tt2 = [63006, 9570, 49216, 45888,
       9822, 23121, 59830, 51114,
       54831, 4189, 580, 5203,
       42174, 59972, 55457, 59009,
       59347, 64456, 8673, 52710,
       49975, 2006, 62677, 3463,
       17754, 5357];
tohex_table = "0123456789abcdef";
def unhex(sc):
    c = ord(sc)
    if (48 <= c and c <= 57):
        return c - 48
    if (65 <= c and c <= 90):
        return c - 55
    if (97 <= c and c <= 122):
        return c - 87
    return 0

def unhex4(s):
    return unhex(s[0])*4096 | unhex(s[1])*256 | unhex(s[2])*16 | unhex(s[3])

def hexToString4(x):
    c = int(x)
    return tohex_table[c>>12 & 15] + tohex_table[c>>8 & 15] + tohex_table[c>>4 & 15] + tohex_table[c>>0 & 15]
def authTransform(val):
    loc3 = val.split("-")
    if (len(loc3)!=2): return val
    if (len(loc3[0])!=8): return val
    if (len(loc3[1])!=8): return val
    loc4 = int("2"+loc3[0][2:8])%(13-int(loc3[0][7:8])-1)
    return (loc3[0]+"-"+hexToString4(tt2[loc4*2+0] ^ unhex4(loc3[1][0:4]))
            +hexToString4(tt2[loc4*2+1] ^ unhex4(loc3[1][4:8])))

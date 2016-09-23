import socket
import thread
import time
import tenhou_auth
import re
import Strategy
com = ""
GameMode = 0
linkerr = 0


def send(data):
    s.send(data)
    print "==========[Me]: " + data + "\n"

command_busy = 0


def timer():
    global linkerr, command_busy
    try:
        while (linkerr == 0):
            if not command_busy: s.send('<Z />\0')
            time.sleep(15)
    except Exception, e:
        linkerr = 1
        print "=== timer linkerror!" + str(e)


def answer_auth(data):
    ind = data.find("auth=") + 6
    auth = data[ind:ind + 17]
    print "pre_auth:" + auth
    auth = tenhou_auth.authTransform(auth)
    print "nxt_auth:" + auth
    send('<AUTH val="' + auth + '"/>\0')


def goto_room(data):
    global GameMode
    fw = open("Bot.log", "a")
    fw.write(data + "\n")
    fw.close()
    send('<GOK />\0')
    send('<NEXTREADY />\0')
    GameMode = 2


def game_logic(data):
    global GameMode, choosen, command_busy
    myturn = 0
    reg = re.findall(r"<([GgEeFfT]\d+)", data)
    if "INIT" in data or "REINIT" in data:
        Strategy.Reach = [0, 0, 0, 0]
        Strategy.discard = [[], [], [], []]
        Strategy.safecard = [[], [], [], []]
        hai = re.search(r'hai="((?:\d+,){12}\d+)"', data).group(1)
        Strategy.hand = [int(i) for i in hai.split(',')]
        tens = re.search(r'ten="((?:\d+,){3}\d+)"', data).group(1)
        Strategy.ten = [int(i) for i in tens.split(',')]
        Strategy.oya = int(data[data.index('oya=') + 5])
        seed = re.search(r'seed="((?:\d+,){5}\d+)"', data).group(1)
        VIPindex = int(seed.split(',')[5])
        Strategy.VIP = [16, 52, 88]
        Strategy.genVIP(VIPindex)
    if "<REACH " in data:
        who = int(data[data.index('who=') + 5])
        Strategy.Reach[who] = 1
    for term in reg:  # lowercase for mo-kiri #!!!!in case <reach><G><T> undone
        if (term[0] in 'GgEeFf'):
            turn = 1 + (term[0] in 'Ff') + (term[0] in 'Gg') * 2
            Strategy.discard[turn] += [int(term[1:])]
            if (term[0] in 'EFG'): Strategy.safecard[turn] = []
            Strategy.safecard[1] += [int(term[1:])]
            Strategy.safecard[2] += [int(term[1:])]
            Strategy.safecard[3] += [int(term[1:])]
        if (term[0] in 'T'):
            Strategy.hand += [int(term[1:])]
            choosen = Strategy.choose_discard(Strategy.hand)
            if Strategy.Reach[0]: choosen = int(term[1:])
            myturn = 1
    if "t=" in data:
        # t(type) and value
        # reach:32 tsumo:16(7) ron:8(6) chi:4(3) kan:2(2) pon:1(1)
        # ankan : type=4? no-t jiakan : type=5 no-t
        t = int(re.search(r't="(\d+)"', data).group(1))
        if (t & 32 and not(1 in Strategy.Reach)) > 0:
            send('<REACH hai="' + str(choosen) + '" />\0')
            return
        elif (t & 8) > 0:
            send('<N type="6" />\0')
            return
        elif (t & 16) > 0:
            send('<N type="7" />\0')
            return
        elif (Strategy.naka(Strategy.hand, int(reg[0][1:]))):
            send('<N type="1" hai0="35" hai1="33" />\0')  # undone
        else:
            send('<N />\0')  # undone
    if myturn or '<REACH who="0"' in data and 'step="2"' not in data:
        send('<D p="' + str(choosen) + '" />\0')
        Strategy.hand.remove(choosen)
        Strategy.discard[0] += [choosen]
    if "<DORA " in data:
        VIPindex = int(re.search(r'hai="(\d+)"', data).group(1))
        Strategy.genVIP(VIPindex)
    if "<N who" in data:
        who = int(data[data.index('who=') + 5])
    if "<AGARI" in data:
        send('<NEXTREADY />\0')
    if "<RYUUKYOKU" in data:
        send('<NEXTREADY />\0')
    if "owari=" in data:
        send('<BYE />\0')
        GameMode = 0


def receiver():
    global com, linkerr
    try:
        while (linkerr == 0):
            data = s.recv(10000)
            if (linkerr != 0): break
            if (len(data) > 2): print "==========[Server]: " + data + "\n"
            if "<HELO un" in data: answer_auth(data)
            if "<REJOIN " in data: send('<JOIN t="' + com + ',r" />\0')
            if "<GO type" in data: goto_room(data)
            if GameMode == 2: game_logic(data)
    except Exception, e:
        linkerr = 1
        print "=== receiver linkerror!" + str(e)

if __name__ == "__main__":
    setfile = open("setting.txt", "w")
    setfile.write("1")
    setfile.close()
    com = raw_input("input room:").rstrip()
    file_set_loop = 1
    while file_set_loop:
        GameMode = 0
        linkerr = 0
        s = socket.socket()
        try:
            s.connect(("133.242.10.78", 10080))
            print "==============================="
            print "|          Connected          |"
            print "==============================="
            thread.start_new_thread(receiver, ())
            thread.start_new_thread(timer, ())
            send('<HELO name="NoName" tid="f0" sx="M" />\0')
            time.sleep(10)
            if (GameMode == 0):
                send('<JOIN t="' + com + '" />\0')
                GameMode = 1
            while (linkerr == 0 and GameMode > 0):
                time.sleep(5)
            if (GameMode == 0):
                setfile = open("setting.txt", "r")
                file_set_loop = int(setfile.readline())
                setfile.close()
        except Exception, e:
            print "=========== Main error =============" + str(e)
            break

"""
ID33ED63F8%2DCE5V8ZBN
ID4B390E99%2DY7aWbR6F
lobby tyep
7   15
3   11
1   9
65  73
----------
x   x
x   x
x   137
x   x
"""

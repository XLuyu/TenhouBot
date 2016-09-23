# -*- coding: utf-8 -*-
import httplib
import urllib
import urllib2
import platform
import os
import re
############## game data #############
Reach = [0, 0, 0, 0]
oya = 0
ten = []
discard = [[], [], [], []]  # 0 for me, 1 for next, 2 for oppo, 3 for last
safecard = [[], [], [], []]  # safecard
mynaka = []  # my nake card
hand = []  # my hand card
VIP = []  # treasure card

exepath = ["phantomjs/", "phantomjs\\"]["indow" in platform.platform()]
exefilename = ["phantomjs", "phantomjs.exe"]["indow" in platform.platform()]


def genVIP(VIPindex):
    global VIP
    index = VIPindex / 4 * 4 + 4
    if (index in [36, 72, 108]): index -= 36
    if (index == 124): index -= 16
    if (index == 136): index -= 12
    VIP += [index, index + 1, index + 2, index + 3]
######################################


def number2char(x):
    if x < 36: return str(x / 4 + 1) + "m"
    elif x < 72: return str((x - 36) / 4 + 1) + "p"
    elif x < 108: return str((x - 72) / 4 + 1) + "s"
    else: return str((x - 108) / 4 + 1) + "z"


def char2number34(x):
    if x[1] == 'm': return int(x[0]) - 1
    if x[1] == 'p': return int(x[0]) - 1 + 9
    if x[1] == 's': return int(x[0]) - 1 + 18
    if x[1] == 'z': return int(x[0]) - 1 + 27


def hand2string(hand):
    tiles = ""
    for tile in hand:
        tiles += number2char(tile)
    return tiles


def gen_phantomjs_script(tiles):
    fw = open("%sloadpage_local.js" % (exepath), "w")
    fw.write("""
        var system = require('system');
        var page = require('webpage').create();
        page.open('paili.htm', function(status) {
            page.evaluate(function(){
                document.querySelector('input[id=tiles]').value = '""" + tiles + """';
                document.querySelector('input[id=submit]').click();
            });
            var ua = page.evaluate(function() {
                return document.getElementById('m2').innerHTML;
            });
            system.stdout.writeLine(ua);
            phantom.exit();
        });
    """)
    fw.close()


def analyse_html(html):
    trs = html.split("<tr ")[1:]
    solus = []
    for tr in trs:
        solu = {}
        pics = tr.split('src="a/')
        n = len(pics)
        solu['discard'] = pics[1][0:2]
        solu['expect'] = [pic[0:2] for pic in pics[2:]]
        num_txt = re.search(r'<td>(\d+)枚</td>', pics[-1:][0]).group(1)
        solu['num'] = int(num_txt)
        solus += [solu]
    return solus


def queryTenhou(hand, evalue):
    gen_phantomjs_script(hand2string(hand))
    html = os.popen("%s%s %sloadpage_local.js" % (exepath, exefilename, exepath)).read()
    # print html
    solus = analyse_html(html)
    #====unify====#
    usedcard = [0 for i in range(34)]
    for i in range(4):
        for tile in discard[i]:
            usedcard[tile / 4] += 1
    for tile in mynaka:
        usedcard[tile / 4] += 1
    maxexp = 0
    for solu in solus:
        for tile in solu['expect']:
            solu['num'] -= usedcard[char2number34(tile)]
        maxexp = max(maxexp, solu['num'])
    for solu in solus:
        for i in range(len(hand)):
            if number2char(hand[i]) == solu['discard']:
                evalue[i] += solu['num'] * 100 / maxexp


def VIP_check(hand, evalue):
    for i in range(len(hand)):
        evalue[i] -= 20 * VIP.count(hand[i])


def defense(hand, evalue):
    for i in range(1, 4):
        if (Reach[i]):
            for j in range(len(hand)):
                for k in range(hand[j] / 4 * 4, hand[j] / 4 * 4 + 4):
                    if (k in safecard[i]) or (k in discard[i]):
                        evalue[j] += 150
                        break


def custom(hand, evalue):
    for i in range(len(hand)):
        if hand[i] >= 108: evalue[i] += 15
        if (hand[i] / 4) in [0, 8, 9, 17, 18, 26]: evalue[i] += 8
        if (hand[i] / 4) in [1, 7, 10, 16, 19, 25]: evalue[i] += 3


def choose_discard(hand):
    evalue = [0 for i in hand]
    queryTenhou(hand, evalue)
    VIP_check(hand, evalue)
    defense(hand, evalue)
    custom(hand, evalue)
    chosen = 0
    for i in range(len(hand)):
        if (evalue[i] > evalue[chosen]): chosen = i
        # print hand[i],evalue[i]
    return hand[chosen]


def naka(hand, card):
    return 0

if __name__ == "__main__":
    hand = [110, 33, 98, 14, 40, 10, 56, 121, 5, 21, 103, 86, 8]
    print choose_discard(hand)

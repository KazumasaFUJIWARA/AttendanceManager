import threading
import time

import nfc

def on_connect(tag):
    # nfc $B%+!<%I@\B3;~$N(Bid$BFI$_<h$j(B($B>.J8;z(B)
    print(tag.identifier.hex())

class Card(object):
    def __init__(self):
        self.flag = False

    def __call__(self):
        with nfc.ContactlessFrontend('usb') as clf:
            while True:
                clf.connect(rdwr={'on-connect': on_connect}, terminate=lambda: self.flag)
                if card.flag:
                    break

threading.Thread(target=(card:=Card())).start()
time.sleep(3)
card.flag=True

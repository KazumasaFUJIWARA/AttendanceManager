import threading
import time

import nfc


class Card(object):
    def __init__(self):
        self.flag = False

    def __call__(self):
        with nfc.ContactlessFrontend('usb') as clf:
            clf.connect(rdwr={}, terminate=lambda: self.flag)

threading.Thread(target=(card:=Card())).start()
time.sleep(1)
card.flag=True

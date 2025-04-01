import tkinter as tk
import nfc

class NFCReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NFC Reader App")

        self.label = tk.Label(root, text="Place NFC card near the reader")
        self.label.pack(pady=20)

    def start_nfc_reading(self):
        # NFCリーダーの設定
        clf = nfc.ContactlessFrontend('usb')

        try:
            # NFCカードが読み取られるまで待機
            tag = clf.connect(rdwr={'on-connect': self.on_connect})
            # 読み取り成功後、再びメッセージを表示して次の読み取りを待機
            self.label.config(text="Place NFC card near the reader")
        except KeyboardInterrupt:
            pass
        finally:
            clf.close()

    def on_connect(self, tag):
        # NFCタグが読み取られたときの処理
        uid = tag.identifier.hex()
        print(f"NFC Tag UID: {uid}")
        self.label.config(text=f"NFC Tag UID: {uid}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NFCReaderApp(root)

    app.start_nfc_reading()

    root.mainloop()

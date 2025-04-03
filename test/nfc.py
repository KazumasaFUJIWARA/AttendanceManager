import nfc
 
# NFCリーダーに接続
def on_connect(tag):
    print(f"カードが接続されました: {tag}")
 
    if isinstance(tag, nfc.clf.ClsFeliCa):
        # FeliCa タグの場合、システム情報を取得
        sys_code = tag.sys_code
        print(f"システムコード: {hex(sys_code)}")
 
        # サービスコードを取得
        for service in tag.services:
            print(f"サービスコード: {hex(service.code)}")
 
            # サービス内のブロックを表示
            for block in service.blocks:
                print(f"  ブロック番号: {hex(block)}")
 
    return True  # 処理続行
 
# リーダーを探して接続
with nfc.ContactlessFrontend('usb') as clf:
    clf.connect(rdwr={'on-connect': on_connect})

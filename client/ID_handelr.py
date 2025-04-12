# -*- coding: utf-8 -*-
import re
from datetime import datetime

#{{{ def read_entry(file_path, key_id):
def read_entry(file_path, key_id):
    # file_path内にkey_idが登録されているか返す
    # 1st return: key_idのある行番号, key_idが登録されていなければ第一変数は-1
    # 2nd return: 第二変数は対応する氏名

    # 検索する行番号-1のカウンター
    row_num=-1

    # 検索値の存在
    detector=0

    # key_idの型調整
    key_id = str(key_id)

    # ファイル全体を読み取る
    with open(file_path, 'r', encoding='UTF-8') as file:
        for line in file:
            row_num += 1
            row_data = line.strip().split('\t')
            if key_id == row_data[0]:
                detector=1
                break
        if detector==0:
            return -1, 0
        else:
            return row_num, row_data[1]
# }}}

# {{{ def remove_register(file_path, line_number):
def remove_register(file_path, line_number):
    # file_pathを一度行ごとにリストに格納してから, 指定された行数を削除
    # no return

    # ファイル全体を読み取る
    with open(file_path, 'r', encoding='UTF-8') as file:
        lines = file.readlines()

    # 指定された行番号を削除
    if 0 <= line_number < len(lines):
        del lines[line_number]

    # ファイルを再度書き込む
    with open(file_path, 'w', encoding='UTF-8') as file:
        file.writelines(lines)
# }}}

#{{{ def add_entry(file_path, key_id, key_name):
def add_entry(file_path, key_id, key_name):
    # file_pathに新規エントリの追加
    # no return

    with open(file_path, 'a', encoding='UTF-8') as file:
        # key_idの型調整
        key_id = str(key_id)
        new_entry = key_id + "\t"+ key_name + "\t0\t0\t0\t0\t0\t0\n"
        file.write(new_entry)
#}}}

#{{{ def add_entry(file_path, entry_name, status):
def add_entry(record_path, entry_name, status):
    # recordに記録を追加
    # no return

    with open(record_path, 'a', encoding='UTF-8') as file:
        # key_idの型調整
        new_record = entry_name + "\t"+ status + "\t" + str(datetime.now()) + "\n"
        file.write(new_entry)
#}}}

#{{{ def update_entry(file_path, key_id):
def update_entry(file_path, key_id):
    # file_pathに新規エントリの追加
    # return: -1 異常終了
    # return: 1 0 0 入室
    # return: 0 hours minutes 退室 滞在時間 滞在分

    entry_num = -1
    #entryにkeyがあるかの識別
    detector = 0

    # ファイル全体を読み取る
    with open(file_path, 'r', encoding='UTF-8') as file:
        entries = file.readlines()

    # ファイル内にkey_idが登録されているか調べる
    with open(file_path, 'r', encoding='UTF-8') as file:
        for line in file:
            entry_num += 1
            # エントリーの情報をタブ区切りで格納
            # 0: ID
            # 1: Name
            # 2: Status
            # 3: Time
            # 4: Core day of week
            # 5: Core lecture time
            # 6: Core day of week
            # 7: Core lecture time
            entry = line.strip().split('\t')

            #検索値があればforから離脱
            if key_id == entry[0]:
                detector = 1
                break

    #検索が失敗した場合は異常終了
    if not detector:
        return -1, 0, 0

    #日付format指定
    date_format = "%Y-%m-%d %H:%M:%S"
    now = datetime.now()

    # 在室不在の状況変更と打刻
    if entry[2] == "0":
        entry[2] = "1"
        entry[3] = now.strftime(date_format)
        hours=0
        minutes=0
    else:
        entry[2] = "0"
        entry_time = datetime.strptime(entry[3], date_format)
        entry[3] = "0"
        # 滞在時間の計算
        stay_time = now - entry_time
        hours, remainder = divmod(stay_time.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

    # entryの新情報を用意
    new_entry='\t'.join(entry) + "\n"

    # entryの新情報を書き出し
    entries[entry_num]=new_entry

    # entryの更新をファイルに書き出し
    with open(file_path, 'w', encoding='UTF-8') as file:
        file.writelines(entries)

    #正常終了
    return int(entry[2]), hours, minutes
# }}}

# TESTな
#  card_info = "Type3Tag 'FeliCa Standard (RC-SA00/1)' ID=01100A0026175C01 PMM=033242828247AAFF SYS=809E"
#  file_path = "List"
#  key_id = id_extracter(card_info)

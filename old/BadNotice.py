# -*- coding: utf-8 -*-
import time
import schedule
import json
import requests

lecture_time=["09:20","11:05","13:35","15:20","17:00","18:40","20:15"]
watch_status = True

# {{{ def time_needle(time_sec):
def time_needle(time_sec):
    if time_sec == 0:
        return "-"
    elif time_sec == 1:
        return "/"
    elif time_sec == 2:
        return "|"
    elif time_sec == 3:
        return "\\"
    elif time_sec == 4:
        return "-"
    elif time_sec == 5:
        return "/"
    elif time_sec == 6:
        return "|"
    else:
        return "\\"
# }}}

# {{{ def webhook_post(webhook_title, webhook_message):
def webhook_post(webhook_title, webhook_message):
    webhook_address = "https://ryu365.webhook.office.com/webhookb2/585cc2b0-ed47-41cd-8bd1-39b5befc07b2@23b65fdf-a4e3-4a19-b03d-12b1d57ad76e/IncomingWebhook/eee629f8a82b4427baf47019708e6b1b/3662ba78-b3f0-47e3-9820-376798dc17d5"
    post_json = json.dumps(
        {
            'title': webhook_title,
            'text': webhook_message
        }
    )
    requests.post(webhook_address, post_json)
#}}}

#{{{ def bad_notice(week_day, lecture_num):
def bad_notice(week_day, lecture_num):
    # file_path内にあるcore timeと在室状況の該当を確認する
    file_path = "List"

    #変数は0からとなっているので調整
    lecture_num += 1
    week_day += 1

    print(f"week_day: {week_day}, lecture_num: {lecture_num}")

    with open(file_path, 'r', encoding='UTF-8') as file:
        for line in file:
            row_data = line.strip().split('\t')
            if row_data[4] == str(week_day):
                if row_data[5] == str(lecture_num):
                    if not int(row_data[2]):
                        webhook_title = "重点: コアタイム違反"
                        webhook_message = row_data[1] + "の在室登録がありません"
                        webhook_post(webhook_title,webhook_message)
            if row_data[6] == str(week_day):
                if row_data[7] == str(lecture_num):
                    if not int(row_data[2]):
                        webhook_title = "重点: コアタイム違反"
                        webhook_message = row_data[1] + "の在室登録がありません"
                        webhook_post(webhook_title,webhook_message)
#}}}

#{{{ schedule.everyで各曜日のスケジュール登録
for lecture_num in range(7):
    print(f"letcute_num: {lecture_num}, lecture_time: {lecture_time[lecture_num]}")
    # lecture_numは時限数-1となっている.
    schedule.every().monday.at(lecture_time[lecture_num]).do(lambda: bad_notice(0,lecture_num))
    schedule.every().tuesday.at(lecture_time[lecture_num]).do(lambda: bad_notice(1,lecture_num))
    schedule.every().wednesday.at(lecture_time[lecture_num]).do(lambda: bad_notice(2,lecture_num))
    schedule.every().thursday.at(lecture_time[lecture_num]).do(lambda: bad_notice(3,lecture_num))
    schedule.every().friday.at(lecture_time[lecture_num]).do(lambda: bad_notice(4,lecture_num))
#}}}

#{{{ Keyboardで中断したらメッセージを吐いて停止
time_sec = 0
while watch_status:
    time_sec += 1
    time_sec = time_sec % 8
    try:
        schedule.run_pending()
        print('\r' + "Waiting" + time_needle(time_sec), end='', flush=True)
        time.sleep(1)
    except KeyboardInterrupt:
        watch_status = False
        print("コアタイムの監視を中断しました")
#}}}

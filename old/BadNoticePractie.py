import time
import schedule

#{{{ def bad_notice(week_day, lecture_num):
def bad_notice(week_day, lecture_num):
    # file_path内にあるcore timeと在室状況の該当を確認する
    file_path = "List"
    lecture_num += 1
    print(f"week_day: {week_day}, lecture_num: {lecture_num}")

    with open(file_path, 'r', encoding='UTF-8') as file:
        for line in file:
            row_data = line.strip().split('\t')
            print(f"{row_data[1]},{row_data[4]},{row_data[6]}")
            if row_data[4] == str(week_day):
                print("week_day matches")
                if row_data[5] == str(lecture_num):
                    print("lecture_num matches")
                    if not int(row_data[2]):
                        print("NOT ATTEND")
#}}}

bad_notice(2, 6)

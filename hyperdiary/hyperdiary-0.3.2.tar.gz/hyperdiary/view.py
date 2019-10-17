def view(diary, date):
    print(date)
    for line in diary.entries[date]:
        print('- ' + str(line))

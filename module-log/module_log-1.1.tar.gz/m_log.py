def create_loglist(string, option, limit):
    list_ = string.split()
    count = 0
    if option == "circular":
        log_list = [0] * limit
        for item in list_:
            if (count >= limit):
                count = 0;
            log_list[count] = item
            count += 1
    if option == "linear":
        log_list = []
        for item in list_:
            if (count < limit):
                log_list.append(item)
                count += 1
    return log_list

abc = create_loglist("aaa bbb ccc ddd eee fff", "linear", 4)
print(abc)

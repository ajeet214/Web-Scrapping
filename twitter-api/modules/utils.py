import datetime

var = [(1, 'Jan'), (2, 'Feb'), (3, 'Mar'), (4, 'Apr'), (5, 'May'), (6, 'Jun'), (7, 'Jul'), (8, 'Aug'),
       (9, 'Sep'), (10, 'Oct'), (11, 'Nov'), (12, 'Dec')]

'''this method converts date sting(like: 'Thu Jun 27 06:52:23 +0000 2019') in unix timestamp'''


def date_formatter(date_string):
    temp_var = date_string.split()
    _year = int(temp_var[-1])
    _day = int(temp_var[2])
    _month = [i[0] for i in var if temp_var[1] in i][0]
    _temp_time = temp_var[3].split(':')
    _hour = int(_temp_time[0])
    _minute = int(_temp_time[1])
    _sec = int(_temp_time[2])
    return int(datetime.datetime(_year, _month, _day, _hour, _minute, _sec).timestamp())


# print(date_formatter('Thu Jun 27 06:52:23 +0000 2019'))



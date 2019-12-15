# -*- coding: utf-8 -*-
"""
thai_time() - Spell out time to Thai words
"""
from datetime import datetime, time
from typing import Union

from pythainlp.util.numtoword import num_to_thaiword
from pythainlp.util.wordtonum import thaiword_to_num
from pythainlp.tokenize import Tokenizer

_TIME_FORMAT_WITH_SEC = "%H:%M:%S"
_TIME_FORMAT_WITHOUT_SEC = "%H:%M"
_DICT_THAI_TIME = {
    "ศูนย์" : 0,
    "หนึ่ง" : 1,
    "สอง" : 2,
    "ยี่" : 2,
    "สาม" : 3,
    "สี่" : 4,
    "ห้า" : 5,
    "หก" : 6,
    "เจ็ด" : 7,
    "แปด" : 8,
    "เก้า" : 9,
    "สิบ" : 10,
    "เอ็ด" : 1,
    # กำหนดค่าของหน่วยเวลา
    "โมงเช้า" : 6, # เริ่มนับ 7:00
    "โมงเย็น" : 13,
    "บ่าย" : 13,
    "บ่ายโมง" : 13,
    "ตี" : 0,
    "เที่ยงวัน" : 12,
    "เที่ยงคืน" : 0,
    "เที่ยง" : 12,
    "ทุ่ม" : 18,
    "นาฬิกา" : 0,
    "ครึ่ง" : 30
}
_THAI_TIME_CUT = Tokenizer(list(_DICT_THAI_TIME.keys()))

def _format_6h(h: int) -> str:
    """
    Thai time (6-hour clock)
    """
    text = ""

    if h == 0:
        text += "เที่ยงคืน"
    elif h < 7:
        text += "ตี" + num_to_thaiword(h)
    elif h < 12:
        text += num_to_thaiword(h - 6) + "โมงเช้า"
    elif h == 12:
        text += "เที่ยง"
    elif h < 18:
        if h == 13:
            text += "บ่ายโมง"
        else:
            text += "บ่าย" + num_to_thaiword(h - 12) + "โมง"
    elif h == 18:
        text += "หกโมงเย็น"
    else:
        text += num_to_thaiword(h - 18) + "ทุ่ม"

    return text


def _format_m6h(h: int) -> str:
    """
    Thai time (modified 6-hour clock)
    """
    text = ""

    if h == 0:
        text += "เที่ยงคืน"
    elif h < 6:
        text += "ตี" + num_to_thaiword(h)
    elif h < 12:
        text += num_to_thaiword(h) + "โมง"
    elif h == 12:
        text += "เที่ยง"
    elif h < 19:
        text += num_to_thaiword(h - 12) + "โมง"
    else:
        text += num_to_thaiword(h - 18) + "ทุ่ม"

    return text


def _format_24h(h: int) -> str:
    """
    Thai time (24-hour clock)
    """
    text = num_to_thaiword(h) + "นาฬิกา"
    return text


def _format(
    h: int,
    m: int,
    s: int,
    fmt: str = "24h",
    precision: Union[str, None] = None,
) -> str:
    text = ""
    if fmt == "6h":
        text = _format_6h(h)
    elif fmt == "m6h":
        text = _format_m6h(h)
    elif fmt == "24h":
        text = _format_24h(h)
    else:
        raise NotImplementedError(fmt)

    if precision == "m" or precision == "s":
        if (
            m == 30
            and (s == 0 or precision == "m")
            and (fmt == "6h" or fmt == "m6h")
        ):
            text += "ครึ่ง"
        else:
            text += num_to_thaiword(m) + "นาที"
            if precision == "s":
                text += num_to_thaiword(s) + "วินาที"
    else:
        if m:
            if m == 30 and s == 0 and (fmt == "6h" or fmt == "m6h"):
                text += "ครึ่ง"
            else:
                text += num_to_thaiword(m) + "นาที"
        if s:
            text += num_to_thaiword(s) + "วินาที"

    return text


def thai_time(
    time_data: Union[time, datetime, str],
    fmt: str = "24h",
    precision: Union[str, None] = None,
) -> str:
    """
    Spell out time to Thai words.

    :param str time_data: time input, can be a datetime.time object \
        or a datetime.datetime object \
        or a string (in H:M or H:M:S format, using 24-hour clock)
    :param str fmt: time output format
        * *24h* - 24-hour clock (default)
        * *6h* - 6-hour clock
        * *m6h* - Modified 6-hour clock
    :param str precision: precision of the spell out
        * *m* - always spell out to minute level
        * *s* - always spell out to second level
        * None - spell out only non-zero parts
    :return: Time spell out in Thai words
    :rtype: str

    :Example:

        thai_time("8:17")
        # output:
        # แปดนาฬิกาสิบเจ็ดนาที

        thai_time("8:17", "6h")
        # output:
        # สองโมงเช้าสิบเจ็ดนาที

        thai_time("8:17", "m6h")
        # output:
        # แปดโมงสิบเจ็ดนาที

        thai_time("18:30", fmt="m6h")
        # output:
        # หกโมงครึ่ง

        thai_time(datetime.time(12, 3, 0))
        # output:
        # สิบสองนาฬิกาสามนาที

        thai_time(datetime.time(12, 3, 0), precision="s")
        # output:
        # สิบสองนาฬิกาสามนาทีศูนย์วินาที
    """
    _time = None

    if isinstance(time_data, time) or isinstance(time_data, datetime):
        _time = time_data
    else:
        if not isinstance(time_data, str):
            raise TypeError(
                "Time data must be a datetime.time object, a datetime.datetime object, or a string."
            )

        if not time_data:
            raise ValueError("Time string cannot be empty.")

        try:
            _time = datetime.strptime(time_data, _TIME_FORMAT_WITH_SEC)
        except ValueError:
            try:
                _time = datetime.strptime(time_data, _TIME_FORMAT_WITHOUT_SEC)
            except ValueError:
                pass

        if not _time:
            raise ValueError(
                f"Time string '{time_data}' does not match H:M or H:M:S format."
            )

    text = _format(_time.hour, _time.minute, _time.second, fmt, precision)

    return text

def thai_time2time(time):
    """
    This function convert thai time into time. (H:M)

    :param str time: thai time

    :return: time
    :rtype: str

    :Example:

        thai_time2time("บ่ายโมงครึ่ง")
        # output:
        # 13:30
    """
    global _THAI_TIME_CUT, _DICT_THAI_TIME
    keys_dict = list(_DICT_THAI_TIME.keys())
    time = time.replace('กว่า','').replace('ๆ','').replace(' ','')
    _i = ["ตีหนึ่ง", "ตีสอง", "ตีสาม", "ตีสี่", "ตีห้า"]
    _time = ""
    for i in ["โมงเช้า", "บ่ายโมง", "โมงเย็น", "โมง", "นาฬิกา", "ทุ่ม","ตี","เที่ยงคืน","เที่ยงวัน","เที่ยง"]:
        if i in time and i!="ตี":
            _time = time.replace(i, i+"|")
            break
        elif i in time and i == "ตี":
            for j in _i:
                if j in time:
                    _time = time.replace(j, j+"|")
                    break
        else:
            pass
    if '|' not in _time:
        raise NotImplementedError()
    _LIST_THAI_TIME = _time.split('|') #_THAI_TIME_CUT.word_tokenize(_time)
    #print(_LIST_THAI_TIME)
    del _time
    hour = _THAI_TIME_CUT.word_tokenize(_LIST_THAI_TIME[0])
    minute = _LIST_THAI_TIME[1]
    if len(minute) > 1:
        minute = _THAI_TIME_CUT.word_tokenize(minute)
    else:
        minute = 0
    time = ""
    #print(hour)
    if hour[-1] == "นาฬิกา" and hour[0] in keys_dict:
        time += str(thaiword_to_num(''.join(hour[:-1])))
    elif hour[0] == "ตี" and hour[1] in keys_dict:
        time += str(_DICT_THAI_TIME[hour[1]])
    elif hour[-1] == "โมงเช้า" and hour[0] in keys_dict:
        if _DICT_THAI_TIME[hour[0]] < 6:
            time += str(_DICT_THAI_TIME[hour[0]]+6)
        else:
            time += str(_DICT_THAI_TIME[hour[0]])
    elif (hour[-1] == "โมงเย็น" or hour[-1] == "โมง") and hour[0] == "บ่าย":
        time += str(_DICT_THAI_TIME[hour[1]]+12)
    elif (hour[-1] == "โมงเย็น" or hour[-1] == "โมง") and hour[0] in keys_dict:
        time += str(_DICT_THAI_TIME[hour[0]]+12)
    elif hour[-1] == "เที่ยงคืน":
        time += "0"
    elif hour[-1] == "เที่ยงวัน" or hour[-1] == "เที่ยง":
        time += "12"
    elif hour[0] == "บ่ายโมง":
        time += "13"
    elif hour[-1] == "ทุ่ม":
        if len(hour) == 1:
            time += "19"
        else:
            time += str(_DICT_THAI_TIME[hour[0]]+18)
    else:
        raise NotImplementedError
    if time == "0":
        time = "00"
    time+=":"
    if minute != 0:
        n = 0
        for i in minute:
            if i in keys_dict:
                if i != "สิบ":
                    n += _DICT_THAI_TIME[i]
                elif i == "สิบ" and n != 0:
                    n *= 10
                elif i == "สิบ" and n == 0:
                    n += 10
        if n != 0 and n > 9:
            time += str(n)
        else:
            time += "0"+str(n)
    return time
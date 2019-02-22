import inflect
import random
import json

p = inflect.engine()
word_to_number_mapping = {}
http_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
all_chars = http_chars + '`~!@#$%*()-_=+[]{}|;:,./?'


def test_json_serialize(val):
    try:
        json.dumps(val)
        return True
    except TypeError:
        return False


def find_in_dict(key, dictionary):
    if key in dictionary:
        return dictionary[key]
    else:
        return None


def text2int(textnum):
    if len(word_to_number_mapping) == 0:
        for i in range(1, 500):
            word_form = p.number_to_words(i)  # 1 -> 'one'
            ordinal_word = p.ordinal(word_form)  # 'one' -> 'first'
            word_to_number_mapping[ordinal_word] = i - 1

    index = -1
    if textnum in word_to_number_mapping:
        index = word_to_number_mapping[textnum]
    return index


def create_random_string(n=20, http_safe=False):
    if http_safe is False:
        chars = all_chars
    else:
        chars = http_chars
    temp_str = "".join([random.SystemRandom().choice(chars) for i in range(n)])
    return temp_str

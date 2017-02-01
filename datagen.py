#!/usr/bin/env python3
import os
from collections import defaultdict
from functools import partial
from pprint import pprint

def cache(fn):
    def inner(*args, **kwargs):
        return fn(*args, **kwargs)
    return inner

def not_implemented(fn):
    def inner(*args, **kwargs):
        print("%s not implemented" % fn.__name__)
        return fn(*args, **kwargs)
    return inner

def unihan_index():
    field_factory = partial(defaultdict, str)

    # unihan is a map of maps to strings
    # the strings default to empty
    unihan = defaultdict(field_factory)
    with open("uni/unihan.txt") as f:
        for line in f:
            if line.startswith("#"):
                continue
            code_point, field, value = line.strip().split('\t')
            code_point = get_char_from_code_point(code_point)
            unihan[code_point][field] = value
    return unihan

def add_frequency(unihan):
    for code, fields in unihan.items():
        if 'kHanyuPinlu' not in fields:
            fields['frequency'] = 0
            continue

        # f_str looks like "ba5(207) ba1(14)" or "zhong1(410)"
        # we'll just combine the two numbers in brackets for simplicity
        f_str =  fields['kHanyuPinlu']

        num_str = ''
        count = 0
        in_bracket = False
        for c in f_str:
            if c == '(':
                in_bracket = True
            elif c == ')':
                in_bracket = False
                count += int(num_str)
                num_str = ''
            elif in_bracket:
                num_str += c

        assert not in_bracket
        assert len(num_str) == 0
        assert count > 0

        fields['frequency'] = count

#==============================================================================
#= This is the api we're kind of going for
#==============================================================================
@not_implemented
def numerical_tone(diacritic_morpheme):
    pass

@not_implemented
def diacritic_tone(numerical_morpheme):
    pass

@not_implemented
def normalize_tone(morpheme, numerical_tones=True, uppercase=False):
    return morpheme.upper()

@not_implemented
def get_image_url(char):
    # Return the url for the given char from the unicode website
    # IE "八" should give http://www.unicode.org/cgi-bin/refglyph?24-516B
    assert len(char) == 1

@not_implemented
def get_pinyin(char, numerical_tones=True, uppercase=False):
    # Return a list of readings for the given character (in order of frequency,
    # where possible)
    # IE "八" should give ["ba1"] (or ["bā"])
    #    "为" should give ["wei4", "wei2"] (or ["wèi", "wéi"])
    assert len(char) == 1

@not_implemented
def get_character(pinyin):
    # Return a list of characters that correspond to the the given reading
    # (in order of frequency where possible, code point otherwise)
    # IE "ba1" should yield ["八", "巴", "扒"]
    pinyin = normalize_tone(pinyin)

def get_definition(char):
    return definition[char]

#==============================================================================
#= ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#==============================================================================

def get_char_from_code_point(code_point):
    assert code_point.startswith('U+')
    for c in code_point[2:]:
        assert c in '0123456789abcdefABCDEF', '%s is not a hex character' % c
    return chr(int(code_point[2:], 16))

@cache
def get_pinyin():
    # Return map of pinyin to unicode characters
    pinyin_map = defaultdict(list)
    for code, fields in unihan.items():
        if 'kMandarin' not in fields:
            continue
        for pinyin in fields['kMandarin'].split():
            pinyin_map[pinyin].append(code)
    return pinyin_map

@cache
def get_definitions():
    # Return map of unicode characters to meanings
    definition = defaultdict(str)
    for code, fields in unihan.items():
        if 'kDefinition' not in fields:
            continue
        definition[code] = fields['kDefinition']
    return definition

def get_definitions_from_file(definition_file):
    definition_map = {}
    for line in definition_file:
        code_point, _, definition = line.strip().split('\t')
        code_point = get_char_from_code_point(code_point)
        definition_map[code_point] = definition
    return definition_map

#filename = input("Filename: ")

#if os.path.isfile(os.path.join('dat', filename)):
#    print("%s already exists" % filename)
#else:
#    print("Creating new file %s" % filename)

data = []

print("Indexing unihan")
unihan = unihan_index()

print("Adding frequencies")
add_frequency(unihan)

print("Creating pinyin index")
pinyin = get_pinyin()

print("Creating definition index")
definition = get_definitions()

while True:
    text = input("Gimme pinyin: ")
    print("You entered %s" % repr(text))
    codes = pinyin[normalize_tone(text)]

    if not codes:
        print("%s is not valid pinyin or no characters match" % repr(text))
        continue

    for code in sorted(codes, key=lambda c: unihan[c]['frequency'], reverse=True):
        response = input("%s (%s): " % (code, unihan[code]['frequency']))
        if response in ['y', 'c']:
            if response == 'y':
                # Now get the definition
                defn = unihan[code]['kDefinition']
                response = input("%s (%s): " % (code, defn)).strip()
                if response:
                    defn = response

                data.append((code, text, defn))
            if response == 'c':
                # Just get the next one
                pass
            break

    pprint(data)
    print()

#while True:
#    pinyin = input("Enter pinyin for the character: ")

import re
import sys


def count_words(lines):
    result = dict()
    wordlist = re.findall(r"[\w']+", " ".join(lines))
    for item in wordlist:
        word = item.lower()
        if word not in result:
            result[word] = 1
        else:
            result[word] += 1
    # Sort alphabetically
    s = sorted(result.items(), key=lambda word: word[0])
    # Sort by number of occurrences
    s = sorted(s, key=lambda word: -word[1])
    return s


if __name__ == '__main__':
    stream = sys.stdin
    lines = sys.stdin.readlines()
    for word, count in count_words(lines):
        print word, count

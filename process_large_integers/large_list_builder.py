#!/usr/bin/python

import argparse
import random


LOWEST = int(1E11)
HIGHEST = int(1E11) + int(1E3)
DATA_VOLUME = 1073741824
MISSING = [100000000990, 100000000977, 100000000961, 100000000962, 100000000961]


class LongStringGenerator:
    """
    Provides some methods to generate data and whatnot
    """
    def __init__(self, lowest=LOWEST, highest=HIGHEST, data_volume=DATA_VOLUME,
            missing=MISSING, separator=' '):
        self.lowest = lowest
        self.highest = highest
        self.data_volume = data_volume
        self.missing = missing
        self.min_digits = len(str(self.lowest))
        self.max_digits = len(str(self.highest))
        self.current_size = 0
        self.separator = separator


    def get_random_number(self, min_val, max_val, missing_numbers):
        number = random.randint(min_val, max_val)
        if number not in missing_numbers:
            return number
        else:
            return self.get_random_number(min_val, max_val, missing_numbers)


    def generate_numbers(self):
        number = self.get_random_number(self.lowest, self.highest, self.missing)
        self.current_size += len(str(number) + self.separator)
        if self.current_size < self.data_volume:
            yield number
        else:
            return


    def write_numbers_to_disk(self):
        with open('large_list.txt', 'wb') as f:
            while self.current_size <= self.data_volume:
                try:
                    f.write(str(self.generate_numbers().next()) + self.separator)
                except StopIteration:
                    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--lowest', dest='lowest', type=int,
        help='Lowest integer')
    parser.add_argument('--highest', dest='highest', type=int,
        help='Highest integer')
    parser.add_argument('--data-volume', dest='data_volume', type=int,
        help='Data volume')
    parser.add_argument('--missing', dest='missing',
          help='Missing integers separated by comma')
    args = parser.parse_args()

    if args.lowest and args.highest and args.data_volume and args.missing:
        l = LongStringGenerator(lowest=args.lowest, highest=args.highest,
            data_volume=args.data_volume, missing=args.missing.split(','))
    else:
        print 'To override the defaults please provide all the arguments'
        l = LongStringGenerator()

    print "writing data to file large_list.txt..."
    l.write_numbers_to_disk()
    print "Done!"


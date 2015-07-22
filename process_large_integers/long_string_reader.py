#!/usr/bin/python


import argparse


TEMPFILES = ['tempfile0001.txt', 'tempfile0002.txt']


class LongStringReader:
    """
    Provides some methods to read and sort the data
    """
    def __init__(self, chunk_size=83886080):
        # 80MB chunks
        self.chunk_size = chunk_size
        self.remainder = ' '
        self.number_of_chunks = self.get_number_of_chunks()
        self.current_chunk = 0
        self.tempfile_counter = 0
        self.tempfiles = TEMPFILES
        self.large_file_name = 'large_list.txt'
        self.number_for_comparison = 0
        # 300MB temp files size
        # TODO: this is not being used at this point, if we are going to try this
        # optimization we should be careful because we may need a lot more memory
        self.tempfile_size = 314572800


    def get_number_of_chunks(self, filename='large_list.txt'):
        import os
        self.number_of_chunks = (
            os.path.getsize('large_list.txt') / self.chunk_size) + 1
        print 'We will use ' + str(self.number_of_chunks) + ' chunks'
        return self.number_of_chunks


    def read_in_chunks(self, file_object):
        while True:
            data = file_object.read(self.chunk_size)
            if not data:
                break
            yield data


    def process_chunk(self, chunk):
        self.current_chunk += 1
        numbers = chunk.split()
        if chunk[0] != ' ':
            numbers[0] = str(self.remainder) + str(numbers[0] + ' ')
        if chunk[-1] != ' ' and self.current_chunk != self.number_of_chunks:
            self.remainder = numbers.pop()
        else:
            self.remainder = ' '
        result = sorted(set(numbers))
        if self.current_chunk == self.number_of_chunks: self.current_chunk = 0
        return result


    def write_tempfiles(self):
        with open(self.large_file_name, 'rb') as f:
            for chunk in self.read_in_chunks(f):
                self.tempfile_counter += 1
                filename = 'tempfile' + "%04d" % self.tempfile_counter + '.txt'
                with open(filename, 'wb') as fw:
                    result = self.process_chunk(chunk)
                    result = '\n'.join([str(item) for item in result])
                    fw.write(result)
            self.tempfile_counter = 0


    def write_result(self):
        missing_integers = []
        import heapq
        self.tempfiles = [
            'tempfile' + "%04d" % i + '.txt' for i in range(
                1, self.number_of_chunks + 1)]
        tempfiles = [open(filename, 'rb') for filename in self.tempfiles]
        for line in heapq.merge(*tempfiles):
            if not self.number_for_comparison:
                self.number_for_comparison = int(line) - 1
            diff = int(line) - int(self.number_for_comparison)
            if diff > 1:
                for i in range(1, diff):
                    missing_integers.append(self.number_for_comparison + i)
            self.number_for_comparison = int(line)
        for filename in tempfiles: filename.close()
        with open('result.txt', 'wb') as f:
            for item in missing_integers:
                f.write(str(item) + '\n')
            print missing_integers
            return missing_integers



if __name__ == '__main__':
    l=LongStringReader()
    print 'Writing tempfiles...'
    l.write_tempfiles()
    print 'Writing result...'
    l.write_result()
    print 'Result written to results.txt'


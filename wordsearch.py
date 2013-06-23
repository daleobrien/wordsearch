#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

Wordsearch.

Create a wordsearch puzzle from a list of words. Optionally, once can add a
second list of words that are included in the puzzle but not in the search key.
In this way near matchs can be added to the puzzle to make it harder to solve.

The WORD_LIST should be a plain text file contianing a single word on each
line. The same goes for the HIDDEN_WORD_LIST.

Usage:
    wordsearch -h
    wordsearch WORD_LIST [HIDDEN_WORD_LIST]
    wordsearch [-l LEVEL] WORD_LIST [HIDDEN_WORD_LIST]

Options:
    -h, --help    Show this help message and exit
    -l, --level   Number of text directions, 1 to 8 [default: 4]

Examples:
    wordsearch -l 3 words.txt

'''
import random
import sys
import string

from docopt import docopt


class Grid(object):

    ENGLISH_LETTERS = string.uppercase[:]

    DIRECTION_CHOICES = ((1, 0),   # left to right
                         (0, 1),   # top to bottom
                         (1, 1),   # diagional, downward
                         (1, -1),  # diagional, upward
                         (0, -1),  # upwards
                         (-1, 0),  # backwards
                         (-1, -1), # diagional, (upward & backwards)
                         (-1, 1))  # diagional, (downward & backwards)

    def __init__(self, options):

        level = 4
        if options['--level']:
            level = int(options['LEVEL'])
            
        # just a small bit of option checking
        if level > len(self.DIRECTION_CHOICES) or level < 1:
            print 'Level must be between 1 and %d' % len(self.DIRECTION_CHOICES)
            print 'You typed %s' % options['LEVEL']
            exit(-1)

        words = open(options['WORD_LIST']).read().splitlines()
        words.sort()

        self.word_list = words
        hidden_words = []

        if options['HIDDEN_WORD_LIST']:
            hidden_words = open(options['HIDDEN_WORD_LIST']).read().splitlines()

        self.hidden_words = [word.upper() for word in hidden_words]    

        self.directions = self.DIRECTION_CHOICES[:level]

        # create the words list, sorted from longest to shortest word
        self.words = [(word.upper(), len(word)) for word in words + hidden_words]
        self.words.sort(key=lambda x: x[1], reverse=True)

        # The grid must be at least as wide as the longest word
        self.wid = self.words[0][1]
        self.hgt = self.wid

        # for latter
        self.max_word_len = self.words[0][1]

        # create data structures
        self.clear()

    def increase_size_by(self, inc):
        self.wid += inc
        self.hgt += inc

    def clear(self):

        self.data = ['.'] * (self.wid * self.hgt)
        self.used = [' '] * (self.wid * self.hgt)
        self.letters = [' '] * (self.wid * self.hgt)

    def to_text(self):
        result = []
        for row in xrange(self.hgt):
            result.append(' '.join(self.data[row * self.wid :
                                  (row + 1) * self.wid]))
        return '\n'.join(result)

    def text(self, solution=False, fancy=True):

        data = self.data
        if solution:
            data = self.letters

        result = []

        left, mid, right = " ", " ", ""
        if fancy:
            result.append("┌─" + "──┬─" * (self.wid - 1) +  "──┐")
            left, mid, right = "│ ", " │ " , " │"
        

        for i, row in enumerate(xrange(self.hgt)):
            result.append(left + mid.join(data[row * self.wid :
                                  (row + 1) * self.wid]) + right)

            if fancy and i < self.hgt - 1:
                result.append("├─" + "──┼─" * (self.wid - 1) +  "──┤")

        if fancy:
            result.append("└─" + "──┴─" * (self.wid - 1) +  "──┘")
        return '\n'.join(result)

    def to_pdf(self, filename):
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter, A4

        pagesize = A4
        paper = canvas.Canvas(filename, pagesize=pagesize)
        margin = 50
        printwid, printhgt = map(lambda x: x - margin * 2, pagesize)
        
        gx = margin
        gy = printhgt - margin
        gdx = printwid / self.wid
        gdy = printhgt / self.hgt

        for y in xrange(self.hgt):
            cy = gy - y * gdy
            for x in xrange(self.wid):
                cx = gx + x * gdx
                p = x + self.wid * y
                c = self.data[p]
                paper.drawString(cx, cy, c)

        paper.showPage()
        paper.save()

    def pick_word_pos(self, wordlen):

        xd, yd = random.choice(self.directions)

        minx = (wordlen - 1, 0, 0)[xd + 1]
        maxx = (self.wid - 1, self.wid - 1, self.wid - wordlen)[xd + 1]
        miny = (wordlen - 1, 0, 0)[yd + 1]
        maxy = (self.hgt - 1, self.hgt - 1, self.hgt - wordlen)[yd + 1]

        x = random.randint(minx, maxx)
        y = random.randint(miny, maxy)

        return x, y, xd, yd

    def write_word(self, word, ox, oy, xd, yd):

        x, y = ox, oy
        for c in word:
            p = x + self.wid * y
            e = self.data[p]
            if e != '.' and e != c:
                return False
            x += xd
            y += yd


        is_a_word_to_for_the_key = True
        if word in self.hidden_words:
            is_a_word_to_for_the_key = False

        x, y = ox, oy
        for c in word:
            p = x + self.wid * y
            self.data[p] = c
            self.used[p] = '.'
            if is_a_word_to_for_the_key:
                self.letters[p] = c
            x += xd
            y += yd

        return True

    def place_words(self, tries=100):

        for word, wordlen in self.words:

            # for each word, have a number of attempts
            local_tries = tries

            while local_tries > 0:

                x, y, xd, yd = self.pick_word_pos(wordlen)

                if self.write_word(word, x, y, xd, yd):
                    # as we go through the list, try harder as the words are 
                    # shorter, so in a way, they are more likely to fit
                    # somewhere
                    tries += 20

                    # next word please
                    break

                local_tries -= 1

            else:
                # we failed to fit this word with the number after trying
                # for 'local_tries'
                return False

        else:
            return True  # all words where placed ...

        # Couldn't place all the words
        return False

    def fill_in_letters(self):

        # TODO: base letters on letter frequency, e.g. ET...
        for p in xrange(self.wid * self.hgt):
            if self.data[p] == '.':
                self.data[p] = random.choice(self.ENGLISH_LETTERS)

    def build(self, tries=100):

        while tries:
            tries -= 1
            self.clear()

            if self.place_words():
                self.fill_in_letters()
                return self

            # every 5th try, increase the gird size
            if tries % 5 == 0:
                self.increase_size_by(1)
        else:
            return None

    def key(self, fancy=True):
        
        pad = 4 if fancy else 2


        number_of_columns = self.wid * pad / (self.max_word_len + 1)

        # print into columns
        words = self.word_list
        
        column_height = len(words) / number_of_columns
        column_width = int(self.wid * pad / number_of_columns)

        # might not be able to fit all the words into exactly 3 columns
        if column_height * number_of_columns != len(words): 
            column_height += 1
        
        results = []
        for i in range(column_height):
            row = " "
            for j in range(number_of_columns):
            
                # last column might not fill up completely
                x = i + j * column_height
                if x < len(words):
                    row += words[x].ljust(column_width)

            results.append(row)

        return "\n".join(results)

if __name__ == '__main__':

    options = docopt(__doc__)

    grid = Grid(options).build()

    if grid is None:
        print "Failed to create a wordsearch puzzle"
    else:
        print
        print grid.text(fancy=True)
        print
        print grid.key(fancy=True)
        print
        print grid.text(solution=True, fancy=True)
        print
    
    #grid.to_pdf("ws.pdf")
    exit(0)

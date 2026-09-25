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
    wordsearch [-l LEVEL] [-p FILE] WORD_LIST [HIDDEN_WORD_LIST]

Options:
    -h, --help                    Show this help message and exit
    -l LEVEL, --level LEVEL       Number of text directions, 1 to 8 [default: 4]
    -p FILE, --pdf FILE           Also write the puzzle to a PDF file

Examples:
    wordsearch -l 3 words.txt
    wordsearch -p puzzle.pdf words.txt hidden.txt

'''
import random
import string

from docopt import docopt


class Grid(object):

    ENGLISH_LETTERS = string.ascii_uppercase[:]

    DIRECTION_CHOICES = ((1, 0),   # left to right
                         (0, 1),   # top to bottom
                         (1, 1),   # diagional, downward
                         (1, -1),  # diagional, upward
                         (0, -1),  # upwards
                         (-1, 0),  # backwards
                         (-1, -1), # diagional, (upward & backwards)
                         (-1, 1))  # diagional, (downward & backwards)

    def __init__(self, options):

        level = int(options['--level'])

        # just a small bit of option checking
        if level > len(self.DIRECTION_CHOICES) or level < 1:
            print('Level must be between 1 and %d' % len(self.DIRECTION_CHOICES))
            print('You typed %s' % options['--level'])
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
        for row in range(self.hgt):
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


        for i, row in enumerate(range(self.hgt)):
            result.append(left + mid.join(data[row * self.wid :
                                  (row + 1) * self.wid]) + right)

            if fancy and i < self.hgt - 1:
                result.append("├─" + "──┼─" * (self.wid - 1) +  "──┤")

        if fancy:
            result.append("└─" + "──┴─" * (self.wid - 1) +  "──┘")
        return '\n'.join(result)

    def to_pdf(self, filename, title="Wordsearch", solution=True):
        """Render the puzzle (and optionally its solution) to a PDF file."""

        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        page_width, page_height = A4
        margin = 45.0
        title_size = 24.0
        title_space = title_size + 30.0
        key_size = 11.0
        key_leading = key_size * 1.6

        usable_width = page_width - margin * 2

        # The key is laid out in as many fixed-width columns as will fit.
        word_column_width = (self.max_word_len + 2) * key_size * 0.6
        key_columns = max(1, int(usable_width // word_column_width))
        key_rows = -(-len(self.word_list) // key_columns)  # round up
        key_height = key_rows * key_leading

        # Size each (square) cell so the title, grid and key all fit on the
        # page. If that leaves no room, fall back to fitting the grid alone.
        cell = usable_width / self.wid
        available = page_height - margin * 2 - title_space - key_height - 20.0
        cell = min(cell, available / self.hgt)
        if cell <= 0:
            cell = usable_width / self.wid

        grid_width = cell * self.wid
        grid_height = cell * self.hgt
        grid_left = (page_width - grid_width) / 2
        grid_top = page_height - margin - title_space

        paper = canvas.Canvas(filename, pagesize=A4)
        paper.setTitle(title)

        # Page one: the puzzle and the list of words to find.
        paper.setFont("Helvetica-Bold", title_size)
        paper.drawCentredString(page_width / 2, page_height - margin - title_size, title)

        self.draw_pdf_grid(paper, self.data, grid_left, grid_top, cell)

        key_top = grid_top - grid_height - 25.0
        self.draw_pdf_key(paper, margin, key_top, key_size, key_leading, key_columns)
        paper.showPage()

        # Page two: the solution grid, with only the key words shown.
        if solution:
            paper.setFont("Helvetica-Bold", title_size)
            paper.drawCentredString(page_width / 2,
                                    page_height - margin - title_size,
                                    "Solution")
            self.draw_pdf_grid(paper, self.letters, grid_left, grid_top, cell)
            paper.showPage()

        paper.save()

    def draw_pdf_grid(self, paper, data, left, top, cell):
        """Draw a letter grid onto a reportlab canvas."""

        width = cell * self.wid
        height = cell * self.hgt

        # Grid lines: light grey interior, solid black border.
        paper.setLineWidth(0.4)
        paper.setStrokeColorRGB(0.65, 0.65, 0.65)
        for col in range(self.wid + 1):
            x = left + col * cell
            paper.line(x, top, x, top - height)
        for row in range(self.hgt + 1):
            y = top - row * cell
            paper.line(left, y, left + width, y)

        paper.setLineWidth(1.2)
        paper.setStrokeColorRGB(0, 0, 0)
        paper.rect(left, top - height, width, height)

        # Letters, centred in each cell. Blank cells are left empty so the
        # solution page only shows the words that were placed.
        font_size = cell * 0.62
        paper.setFont("Courier-Bold", font_size)
        paper.setFillColorRGB(0, 0, 0)
        for row in range(self.hgt):
            for col in range(self.wid):
                c = data[col + self.wid * row]
                if c == ' ':
                    continue
                x = left + col * cell + cell / 2
                y = top - row * cell - cell / 2 - font_size * 0.36
                paper.drawCentredString(x, y, c)

    def draw_pdf_key(self, paper, left, top, font_size, leading, columns):
        """Draw the word key in fixed-width columns, top to bottom."""

        paper.setFont("Courier-Bold", font_size)
        paper.setFillColorRGB(0, 0, 0)

        rows = -(-len(self.word_list) // columns)  # round up
        column_width = (self.max_word_len + 2) * font_size * 0.6

        for index, word in enumerate(self.word_list):
            col = index // rows
            row = index % rows
            x = left + col * column_width
            y = top - (row + 1) * leading
            paper.drawString(x, y, word)

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
        for p in range(self.wid * self.hgt):
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


        number_of_columns = self.wid * pad // (self.max_word_len + 1)

        # print into columns
        words = self.word_list

        column_height = len(words) // number_of_columns
        column_width = self.wid * pad // number_of_columns

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

def main():

    options = docopt(__doc__)

    grid = Grid(options).build()

    if grid is None:
        print("Failed to create a wordsearch puzzle")
        exit(1)

    print()
    print(grid.text(fancy=True))
    print()
    print(grid.key(fancy=True))
    print()
    print(grid.text(solution=True, fancy=True))
    print()

    if options['--pdf']:
        grid.to_pdf(options['--pdf'])
        print('Wrote %s' % options['--pdf'])

    exit(0)


if __name__ == '__main__':
    main()

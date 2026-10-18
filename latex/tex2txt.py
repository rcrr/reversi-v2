#!/usr/bin/env python3
#
# tex2txt.py
#
# This file is part of the reversi program
# http://github.com/rcrr/reversi-v2
#
# Author Roberto Corradini mailto:rob_corradini@yahoo.it
# Copyright 2026 Roberto Corradini. All rights reserved.
#
# License
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
# or visit the site <http://www.gnu.org/licenses/>.
#

"""tex2txt.py — strip LaTeX markup to plain *prose*, for the Italian spellcheck (G8).

Reads a .tex file on stdin, writes the human-readable prose on stdout.
A spell *filter*, not a general LaTeX->text converter (that would be pandoc).

It removes, so aspell sees only real prose:
  * comments            (% to end of line, unless escaped as \\%)
  * environments        (\\begin{..} / \\end{..})
  * [option] groups     (\\usepackage[utf8]{inputenc} -> the options vanish)
  * structural commands (\\documentclass, \\usepackage, \\include, \\title, \\label, ...)
    together with their {argument}
Then it keeps the {argument} of every remaining command (\\chapter{X} -> X) and
drops the leftover braces. Domain terms you want allowed (pattern, bitboard, board,
D8, ...) belong in dict.txt (the personal dictionary), not here.
"""
import re
import sys

# Commands whose arguments are NOT prose — drop the command and its {arg}.
NON_PROSE = {
    'documentclass', 'usepackage', 'include', 'includeonly', 'input', 'tableofcontents',
    'maketitle', 'title', 'author', 'date', 'label', 'index', 'bibliography',
    'bibliographystyle', 'addcontentsline', 'setcounter', 'pagestyle', 'thispagestyle',
    'chaptermark', 'sectionmark', 'subsectionmark', 'verb', 'verbatim', 'url', 'href',
    'texttt', 'ttfamily', 'geometry',        # technical content / layout options (NOT bold/italic prose)
}

s = sys.stdin.read()
s = re.sub(r'(?<!\\)%.*', '', s)                          # 1. comments
s = re.sub(r'\\(?:begin|end)\s*\{[^}]*\}', ' ', s)        # 1b. environments
s = re.sub(r'\[[^\]]*\]', ' ', s)                          # 2. [options]
for c in sorted(NON_PROSE, key=len, reverse=True):         # 3. structural commands + {arg}
    s = re.sub(r'\\%s\*?\s*\{[^{}]*\}' % c, ' ', s)
    s = re.sub(r'\\%s\*?' % c, ' ', s)
s = re.sub(r'\\[a-zA-Z]+\*?\s*\{([^{}]*)\}', r'\1', s)    # 4. remaining \cmd{arg} -> arg
s = re.sub(r'\\[a-zA-Z]+\*?', ' ', s)                      # 5. remaining \cmd -> space
s = re.sub(r'\\([{}&%$#_\\])', r'\1', s)                   # 6. escaped specials
s = re.sub(r'[{}]', ' ', s)                                # 7. leftover braces
print(s)

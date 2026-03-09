#!/usr/bin/env python3
"""
scanner_demo.py
===============
Python implementation of the C- lexical analyzer that exactly mirrors
the flex specification in scanner.l.

This file serves two purposes:
  1. Demonstrate/test the scanner logic without requiring flex installed.
  2. Generate the output sections for the report.

Usage:
    python3 scanner_demo.py test1_valid.cm
    python3 scanner_demo.py test2_errors.cm
"""

import sys
import re

# ---------------------------------------------------------------------------
# Token definitions
# ---------------------------------------------------------------------------

KEYWORDS = {"else", "if", "int", "return", "void", "while"}

# Order matters: longer / higher-priority patterns first.
# Each entry: (token_name, regex_pattern)
# We use re.match at the current position, advancing after each match.

# Special characters allowed in identifiers
SPEC_CHARS = r'[.#$_]'
LETTER     = r'[a-zA-Z]'
DIGIT      = r'[0-9]'
ALNUM      = r'[a-zA-Z0-9]'

TOKEN_PATTERNS = [
    # Multi-char operators (before single-char ones)
    ("LTE",      r'<='),
    ("GTE",      r'>='),
    ("EQ",       r'=='),
    ("NEQ",      r'!='),
    # Single-char operators / punctuation
    ("PLUS",     r'\+'),
    ("MINUS",    r'-'),
    ("TIMES",    r'\*'),
    ("DIVIDE",   r'/'),
    ("LT",       r'<'),
    ("GT",       r'>'),
    ("ASSIGN",   r'='),
    ("SEMI",     r';'),
    ("COMMA",    r','),
    ("LPAREN",   r'\('),
    ("RPAREN",   r'\)'),
    ("LBRACKET", r'\['),
    ("RBRACKET", r'\]'),
    ("LBRACE",   r'\{'),
    ("RBRACE",   r'\}'),
]

# Compiled patterns for identifiers and numbers
RE_COMMENT_OPEN = re.compile(r'/\*')
RE_VALID_ID     = re.compile(
    rf'{LETTER}(?:{LETTER}|{DIGIT})*(?:{SPEC_CHARS}{ALNUM}+)?')
RE_WRONG_ID     = re.compile(
    rf'{LETTER}(?:{LETTER}|{DIGIT})*{SPEC_CHARS}')
RE_VALID_NUM    = re.compile(
    rf'(?:{DIGIT}+\.{DIGIT}*|{DIGIT}+)(?:[Ee][+\-]?{DIGIT}+)?')
RE_WRONG_NUM    = re.compile(
    rf'(?:{DIGIT}+\.{DIGIT}*|{DIGIT}+)[Ee][+\-]')
RE_NEWLINE      = re.compile(r'\n')
RE_WHITESPACE   = re.compile(r'[ \t\r]+')

COMPILED_OPS = [(name, re.compile(pat)) for name, pat in TOKEN_PATTERNS]

# Characters that are legal in the language alphabet
VALID_CHARS = set(
    'abcdefghijklmnopqrstuvwxyz'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    '0123456789'
    ' \t\n\r'
    '+-*/<>=!;,()[]{}.'
    '#$_'
)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def print_token(line, col, name, lexeme):
    print(f"Line {line:3d}, Col {col:3d} | Token: {name:<12s} | Lexeme: \"{lexeme}\"")

def print_error(line, col, msg, file=sys.stderr):
    print(f"LEXICAL ERROR [Line {line}, Col {col}]: {msg}", file=file)

# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

def scan(source: str, filename: str = "<stdin>"):
    print(f"Scanning: {filename}\n")
    print(f"{'Position':<25} {'Token':<14} Lexeme")
    print(f"{'-'*25} {'-'*14} {'-'*30}")

    pos       = 0
    line_num  = 1
    col_num   = 1
    n         = len(source)

    def advance(length):
        """Move pos/line_num/col_num forward by `length` chars."""
        nonlocal pos, line_num, col_num
        for ch in source[pos:pos + length]:
            if ch == '\n':
                line_num += 1
                col_num = 1
            else:
                col_num += 1
        pos += length

    while pos < n:
        # ---- 1. Comments ------------------------------------------------
        m = RE_COMMENT_OPEN.match(source, pos)
        if m:
            cmt_line, cmt_col = line_num, col_num
            advance(2)           # consume '/*'
            closed = False
            while pos < n - 1:
                if source[pos] == '*' and source[pos + 1] == '/':
                    advance(2)   # consume '*/'
                    closed = True
                    break
                advance(1)
            else:
                # consume whatever is left
                advance(n - pos)

            if not closed:
                print_error(line_num, col_num,
                    f"Reached end of file inside unclosed comment "
                    f"(comment opened at line {cmt_line}, col {cmt_col})")
            continue

        # ---- 2. Newline -------------------------------------------------
        if source[pos] == '\n':
            line_num += 1
            col_num = 1
            pos += 1
            continue

        # ---- 3. Other whitespace ----------------------------------------
        m = RE_WHITESPACE.match(source, pos)
        if m:
            advance(m.end() - pos)
            continue

        # ---- 4. Keywords / Identifiers ----------------------------------
        #
        # Try VALID_ID and WRONG_ID; pick longest match, valid wins on tie.
        m_valid = RE_VALID_ID.match(source, pos)
        m_wrong = RE_WRONG_ID.match(source, pos)

        len_valid = m_valid.end() - pos if m_valid else 0
        len_wrong = m_wrong.end() - pos if m_wrong else 0

        if len_valid > 0 or len_wrong > 0:
            tok_line, tok_col = line_num, col_num
            if len_valid >= len_wrong:
                # Valid ID (or keyword)
                lexeme = m_valid.group()
                advance(len_valid)
                if lexeme in KEYWORDS:
                    print_token(tok_line, tok_col, lexeme.upper(), lexeme)
                else:
                    print_token(tok_line, tok_col, "ID", lexeme)
            else:
                # Wrong ID
                lexeme = m_wrong.group()
                advance(len_wrong)
                print_error(tok_line, tok_col,
                    f"Invalid identifier \"{lexeme}\" -- "
                    f"special character '{lexeme[-1]}' must be "
                    f"followed by a letter or digit")
            continue

        # ---- 5. Numbers -------------------------------------------------
        m_vnum = RE_VALID_NUM.match(source, pos)
        m_wnum = RE_WRONG_NUM.match(source, pos)

        len_vnum = m_vnum.end() - pos if m_vnum else 0
        len_wnum = m_wnum.end() - pos if m_wnum else 0

        # Only consider a zero-length valid-num match as no-match
        if len_vnum > 0 or len_wnum > 0:
            tok_line, tok_col = line_num, col_num
            if len_vnum >= len_wnum:
                lexeme = m_vnum.group()
                advance(len_vnum)
                print_token(tok_line, tok_col, "NUM", lexeme)
            else:
                lexeme = m_wnum.group()
                advance(len_wnum)
                print_error(tok_line, tok_col,
                    f"Invalid number \"{lexeme}\" -- "
                    f"exponent sign must be immediately followed by "
                    f"one or more digits")
            continue

        # ---- 6. Operators / Punctuation ---------------------------------
        matched_op = False
        for name, pattern in COMPILED_OPS:
            m = pattern.match(source, pos)
            if m:
                tok_line, tok_col = line_num, col_num
                lexeme = m.group()
                advance(len(lexeme))
                print_token(tok_line, tok_col, name, lexeme)
                matched_op = True
                break
        if matched_op:
            continue

        # ---- 7. Invalid character ---------------------------------------
        tok_line, tok_col = line_num, col_num
        ch = source[pos]
        print_error(tok_line, tok_col,
            f"Invalid character '{ch}' (ASCII {ord(ch)}) -- "
            f"not in the language alphabet")
        advance(1)

    print("\n[Done]")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        try:
            with open(fname, 'r') as f:
                src = f.read()
        except OSError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        fname = "<stdin>"
        src = sys.stdin.read()

    scan(src, fname)

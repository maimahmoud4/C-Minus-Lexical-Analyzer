# C⁻ Lexical Analyzer

A lexical scanner for the **C⁻** programming language, built with **GNU Flex** as part of a Compiler Design course assignment.

The scanner reads C⁻ source files, outputs a labeled token stream, and reports four categories of lexical error with precise line and column diagnostics.

---

## Token Types

| Category | Tokens |
|---|---|
| Keywords | `ELSE` `IF` `INT` `RETURN` `VOID` `WHILE` |
| Identifiers | `ID` |
| Numbers | `NUM` |
| Operators | `PLUS` `MINUS` `TIMES` `DIVIDE` `LT` `LTE` `GT` `GTE` `EQ` `NEQ` `ASSIGN` |
| Punctuation | `SEMI` `COMMA` `LPAREN` `RPAREN` `LBRACKET` `RBRACKET` `LBRACE` `RBRACE` |

### Modified Definitions

```
ID  = letter (letter | digit)* ( [.#$_] (letter | digit)+ )?
NUM = (digit+ | digit+ "." digit*) ( (E|e) (+|-)? digit+ )?
```

---

## Error Handling

| # | Error | Example |
|---|---|---|
| 1 | EOF inside unclosed comment | `/* not closed` |
| 2 | Character not in the language alphabet | `@` `^` `?` |
| 3 | Invalid identifier (bare special character) | `a#` `b.` `c$` |
| 4 | Invalid number (exponent sign with no digits) | `23e+` `5.0E-` |

---

## Project Structure

```
.
├── scanner.l                        # Flex specification (main source)
├── scanner.exe                      # Compiled executable (Windows)
├── scanner_demo.py                  # Python mirror of the scanner (no flex required)
├── Makefile                         # Build and test automation
├── test1_valid.cm                   # Test input: valid C⁻ program
├── test2_errors.cm                  # Test input: all four error categories
└── Assignment1_lex_Mai_Mahmoud.pdf  # Report
```

---

## Requirements

- [GNU flex](https://github.com/westes/flex) 2.6+
- GCC (or any C99-compatible compiler)
- GNU make

**Install flex:**
```bash
# Ubuntu / Debian
sudo apt install flex

# macOS
brew install flex

# Windows
# Use MSYS2/MinGW or WSL
```

---

## Build

```bash
make
```

This runs `flex scanner.l` then compiles `lex.yy.c` into the `scanner` executable.

---

## Usage

```bash
# Scan a file
./scanner input_file.cm

# Read from stdin
./scanner

# Run both test cases
make test

# Clean build artifacts
make clean
```

---

## Output Format

Tokens are printed to **stdout**:
```
Line   L, Col   C | Token: TOKEN_NAME   | Lexeme: "lexeme"
```

Lexical errors are printed to **stderr**:
```
LEXICAL ERROR [Line L, Col C]: <descriptive message>
```

### Example

Input:
```c
int gcd(int u, int v) {
    if (v == 0) return u;
}
```

Output:
```
Line   1, Col   1 | Token: INT          | Lexeme: "int"
Line   1, Col   5 | Token: ID           | Lexeme: "gcd"
Line   1, Col   8 | Token: LPAREN       | Lexeme: "("
Line   1, Col   9 | Token: INT          | Lexeme: "int"
Line   1, Col  13 | Token: ID           | Lexeme: "u"
...
```

---

## Notes

- Scanning continues after errors of types 2–4, maximising diagnostics in a single pass.
- A sequence like `12ab` produces `NUM "12"` then `ID "ab"` — this is intentional; the error is syntactic and handled by the parser.
- The harmless compiler warning `'yyunput' defined but not used` can be suppressed by adding `%option nounput` to `scanner.l`.

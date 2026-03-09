# Makefile for C- Lexical Analyzer
# Usage:
#   make          – build the scanner executable
#   make test     – run all test cases
#   make clean    – remove generated files

CC      = gcc
CFLAGS  = -Wall -Wextra -g
TARGET  = scanner
LEX     = flex

.PHONY: all test clean

all: $(TARGET)

# Step 1: flex generates lex.yy.c from scanner.l
lex.yy.c: scanner.l
	$(LEX) scanner.l

# Step 2: compile the generated C file
$(TARGET): lex.yy.c
	$(CC) $(CFLAGS) -o $(TARGET) lex.yy.c

# Run both test files and save combined output
test: $(TARGET)
	@echo "===== TEST 1: Valid C- Program ====="
	./$(TARGET) test1_valid.cm
	@echo ""
	@echo "===== TEST 2: Error Cases ====="
	./$(TARGET) test2_errors.cm

clean:
	rm -f lex.yy.c $(TARGET)

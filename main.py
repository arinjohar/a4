from typing import * # type: ignore
from dataclasses import dataclass
import unittest
import sys
import string # type: ignore
sys.setrecursionlimit(10**6)

IntList : TypeAlias = Union[None, 'IntNode']

@dataclass(frozen=True)
class IntNode:
    value : int
    rest : IntList

@dataclass(frozen=False)
class WordLines:
    key : str
    line_nums : IntList

WordLinesList : TypeAlias = Union[None, 'WordLinesNode']

@dataclass(frozen=True)
class WordLinesNode:
    value : WordLines
    rest : WordLinesList

@dataclass(frozen=False)
class HashTable:
    array : List[WordLinesList]
    count : int

# Return the hash code of 's' (see assignment description).
def hash_fn(s: str) -> int:
    h = 0
    for char in s:
        h = h * 31 + ord(char)
    return h

# Make a fresh hash table with the given number of bins 'size',
# containing no elements.
def make_hash(size: int) -> HashTable:
    return HashTable(array=[None] * size, count=0)

# Return the number of bins in 'ht'.
def hash_size(ht: HashTable) -> int:
    return len(ht.array)

# Return the number of elements (key-value pairs) in 'ht'.
def hash_count(ht: HashTable) -> int:
    return ht.count

# Return whether 'ht' contains a mapping for the given 'word'.
def has_key(ht: HashTable, word: str) -> bool:
    index = hash_fn(word) % hash_size(ht)
    current = ht.array[index]
    
    while current is not None:
        if current.value.key == word:
            return True
        current = current.rest
    return False

# Helper to check if a line number is already in the IntList.
def line_exists(lines: IntList, line: int) -> bool:
    curr = lines
    while curr is not None:
        if curr.value == line:
            return True
        curr = curr.rest
    return False

# Return the line numbers associated with the key 'word' in 'ht'.
# The returned list should not contain duplicates, but need not be sorted.
def lookup(ht: HashTable, word: str) -> List[int]:
    index = hash_fn(word) % hash_size(ht)
    curr = ht.array[index]
    while curr is not None:
        if curr.value.key == word:
            result = []
            line_node = curr.value.line_nums
            while line_node is not None:
                result.append(line_node.value) # type: ignore
                line_node = line_node.rest
            return result # type: ignore
        curr = curr.rest
    return []

# Record in 'ht' that 'word' has an occurrence on line 'line'.
def add(ht: HashTable, word: str, line: int) -> None:
    index = hash_fn(word) % hash_size(ht)
    curr = ht.array[index]
    
    # 1. Check if word exists
    while curr is not None:
        if curr.value.key == word:
            # Word found: add line if it's not a duplicate 
            if not line_exists(curr.value.line_nums, line):
                curr.value.line_nums = IntNode(line, curr.value.line_nums)
            return 
        curr = curr.rest
    
    # 2. Word not found: add new WordLines entry
    new_entry = WordLines(word, IntNode(line, None))
    ht.array[index] = WordLinesNode(new_entry, ht.array[index])
    ht.count += 1
    
    # 3. Check load factor for resize (Threshold = 1.0)
    if ht.count >= hash_size(ht):
        resize_hash_table(ht)

# Helper function that resizes 'ht' if necessary
def resize_hash_table(ht: HashTable) -> None:
    old_array = ht.array
    new_size = len(old_array) * 2 
    ht.array = [None] * new_size
    ht.count = 0 
    
    for bin_node in old_array:
        curr_word_node = bin_node
        while curr_word_node is not None:
            lines = curr_word_node.value.line_nums
            while lines is not None:
                add(ht, curr_word_node.value.key, lines.value)
                lines = lines.rest
            curr_word_node = curr_word_node.rest

# Return the words that have mappings in 'ht'.
# The returned list should not contain duplicates, but need not be sorted.
def hash_keys(ht: HashTable) -> List[str]:
    keys = []
    for bin_head in ht.array:
        curr = bin_head
        while curr is not None:
            keys.append(curr.value.key) # type: ignore
            curr = curr.rest
    return keys # type: ignore

# Given a hash table 'stop_words' containing stop words as keys, plus
# a sequence of strings 'lines' representing the lines of a document,
# return a hash table representing a concordance of that document.
def make_concordance(stop_words: HashTable, lines: List[str]) -> HashTable:
    concordance = make_hash(128) 
    
    for line_idx, line_text in enumerate(lines):
        line_num = line_idx + 1 
        
        cleaned = line_text.replace("'", "")
        
        for char in string.punctuation:
            if char != "'": 
                cleaned = cleaned.replace(char, " ")
        
        tokens = cleaned.lower().split()
        
        for token in tokens:
            if token.isalpha():
                if not has_key(stop_words, token):
                    add(concordance, token, line_num)
                    
    return concordance

# Given an input file path, a stop-words file path, and an output file path,
# overwrite the indicated output file with a sorted concordance of the input file.
def full_concordance(in_file: str, stop_words_file: str, out_file: str) -> None:
    stop_words_ht = make_hash(128)
    try:
        with open(stop_words_file, 'r') as f:
            for line in f:
                for word in line.lower().split():
                    add(stop_words_ht, word, 0) 
    except FileNotFoundError:
        pass 

    with open(in_file, 'r') as f:
        input_lines = f.readlines()

    concordance = make_concordance(stop_words_ht, input_lines)

    sorted_keys = sorted(hash_keys(concordance))

    with open(out_file, 'w') as f:
        for i, key in enumerate(sorted_keys):
            line_nums = lookup(concordance, key)

            line_nums.sort()
            
            line_str = " ".join(map(str, line_nums))
            f.write(f"{key}: {line_str}")
            
            if i < len(sorted_keys) - 1:
                f.write("\n")

class Tests(unittest.TestCase):
    def test_hash_fn(self):
        self.assertEqual(hash_fn("abc"), (ord('a')*31**2 + ord('b')*31**1 + ord('c')))

    def test_make_hash(self):
        ht = make_hash(128)
        self.assertEqual(hash_size(ht), 128) 
        self.assertEqual(hash_count(ht), 0) 

    def test_add_and_lookup(self):
        ht = make_hash(10)
        add(ht, "test", 1)
        add(ht, "test", 2)
        add(ht, "test", 1) 
        self.assertEqual(lookup(ht, "test"), [2, 1]) 
        self.assertTrue(has_key(ht, "test")) 

    def test_resize(self):
        ht = make_hash(2)
        add(ht, "one", 1)
        add(ht, "two", 2) 
        self.assertEqual(hash_size(ht), 4)
        self.assertEqual(hash_count(ht), 2)

    def test_make_concordance(self):
        stop_words = make_hash(10)
        add(stop_words, "is", 0) 
        lines = ["This is a test.", "Test this!"]
        ht = make_concordance(stop_words, lines)
        self.assertFalse(has_key(ht, "is")) 
        self.assertTrue(has_key(ht, "test"))
        self.assertEqual(len(hash_keys(ht)), 3)

    def test_sample_files(self):
        full_concordance("sampletext.txt", "samplestopwords.txt", "output.txt")
        with open("output.txt", "r") as f:
            content = f.read()
            self.assertIn("data: 1 4", content)
            self.assertIn("sample: 1", content)

if (__name__ == '__main__'):
    unittest.main()
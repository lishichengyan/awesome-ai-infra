"""
1. Initialization: Use a text corpus. Split each word in the corpus into individual characters.
    For example, the word “hello” becomes “h e l l o”.
    The initial vocabulary consists of all unique characters in the corpus.
2. Iterative merging:
    2.1 Count adjacent symbol pairs: Treat each character as a symbol.
        Go through the corpus and count every pair of adjacent symbols.
        For example, in “h e l l o”, the pairs are “h e”, “e l”, “l l”, “l o”.
    2.3 Select the most frequent symbol pair: Identify the pair with the
        highest count in the entire corpus. For instance, if “l l” occurs
        most frequently, select it.
    2.4 Merge the selected pair: Replace all occurrences of the most frequent symbol pair with
        a new single merged symbol. For example, “l l” would be replaced with
        a new merged symbol “ll”. The word “h e l l o” now becomes “h e ll o”.
    2.5 Update the vocabulary: Add the new merged symbol to the vocabulary. The vocabulary now
        includes the original characters and the new symbol “ll”.
3. Repeat: Continue the iterative merging until the vocabulary reaches the desired size.

example:
("hug", 10), ("pug", 5), ("pun", 12), ("bun", 4), ("hugs", 5)
=>
("h" "u" "g", 10), ("p" "u" "g", 5), ("p" "u" "n", 12), ("b" "u" "n", 4), ("h" "u" "g" "s", 5)
=>
Vocabulary: ["b", "g", "h", "n", "p", "s", "u", "ug"]
Corpus: ("h" "ug", 10), ("p" "ug", 5), ("p" "u" "n", 12), ("b" "u" "n", 4), ("h" "ug" "s", 5)
=>
Vocabulary: ["b", "g", "h", "n", "p", "s", "u", "ug", "un"]
Corpus: ("h" "ug", 10), ("p" "ug", 5), ("p" "un", 12), ("b" "un", 4), ("h" "ug" "s", 5)
=>
Vocabulary: ["b", "g", "h", "n", "p", "s", "u", "ug", "un", "hug"]
Corpus: ("hug", 10), ("p" "ug", 5), ("p" "un", 12), ("b" "un", 4), ("hug" "s", 5)
"""

from collections import defaultdict


def initialize_vocabulary(corpus):
    """
    Creates initial vocabulary from corpus by splitting words into characters.
    Adds word boundary marker '_' and tracks unique characters.

    Args:
        corpus (iterable): Iterator or list of words to process

    Returns:
        tuple: (vocabulary dict mapping tokenized words to counts,
               set of unique characters in corpus)
    """
    # Track word counts and unique characters
    vocabulary = defaultdict(int)
    charset = set()

    for word in corpus:
        # Add word boundary marker and split into characters
        word_with_marker = "_" + word
        characters = list(word_with_marker)
        # Update set of unique characters
        charset.update(characters)
        # Create space-separated string of characters
        tokenized_word = " ".join(characters)
        # Increment count for this tokenized word
        vocabulary[tokenized_word] += 1

    return vocabulary, charset


print(initialize_vocabulary("hello world"))

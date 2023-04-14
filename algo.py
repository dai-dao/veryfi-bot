from typing import List, Optional


"""
Given an arbitrary input string from the user, extract the list of anagram strings
the anagrams should only be lowercase alphabet letters

Input:
    Please group the anagrams in this list ["affx", "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]
    
Output:
    ["affx", "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]
    
Can also handle cases where there are extra characters like [ and ]
    - Please group [just to test] the anagrams in this list ["affx", "a", 'ab', "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]
Can detect syntax error in the list expression like
    - Group the [] anagrams in this list "affx", "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]
    - Group the anagrams in this list [", "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]
    - Group ] the anagrams in this list ["affx" "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]
    - Group [ the anagrams in this list ["aff\nx", "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]
    - Group [ the anagrams ] in this list ["aff  x", "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]
    - Group the anagrams in this list ["affx", "a", "ab', "ba", "nnx", "xnn", "cde', "edc", "dce", "xffa"]
    
Analysis:

    - runtime: Make one pass across the input string, O(n)
        - the while loops help locate the correct [ and ] indicating the correct list expressions
        - since it's scanning from left to right, runtime is still O(n)
    - space  : 
        - keep track of building the current word
        - store the output anagram list O(n)
"""
def extract_anagram_list_from_input(input : str) -> Optional[List[str]]:
    def evaluate_list_string(input : str, list_open_bracket_offset, list_close_bracket_offset) -> Optional[List[str]]:
        if list_open_bracket_offset >= list_close_bracket_offset:
            return None
        open_quote = ''
        new_word_found = False
        current_word = ""
        out = []
        for char in input[list_open_bracket_offset + 1 : list_close_bracket_offset] :
            if new_word_found:
                # the next character allowed after a word was identified must be ',' or ' '
                if char not in [",", " "]:
                    return None # Syntax error
                elif char == ",":
                    new_word_found = False
                    continue

            if char in ["'", "\""]:
                if open_quote == '':
                    open_quote = char
                else:
                    if char != open_quote:
                        return None # word open and close quote must be the same
                    open_quote = ''
                    out.append(current_word)
                    current_word = ""
                    new_word_found = True
            elif char == " ":
                if open_quote:
                    return None # Can not have empty space in word
                continue                   
            elif ord(char) >= 97 and ord(char) <= ord("z"):
                current_word += char
            else:
                return None # Syntax error            
            
        return out
    
    
    if "[" not in input or "]" not in input:
        return None
    
    # Sanitize
    input = input.replace("\n", " ").replace("\t", " ").replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'")
    # Input string can have arbitrary [ ] all over , need to find the [ ] corresponding to the list expression
    list_open_bracket_offset = input.index("[")
    list_close_bracket_offset = input.index("]")
    while list_close_bracket_offset <= list_open_bracket_offset and "]" in input[list_close_bracket_offset + 1:]:
        list_close_bracket_offset = list_close_bracket_offset + 1 + input[list_close_bracket_offset + 1:].index("]")
    # Keep finding the next [ character until a valid list expression is found
    out = evaluate_list_string(input, list_open_bracket_offset, list_close_bracket_offset)
    while not out and "[" in input[list_open_bracket_offset + 1:]:
        list_open_bracket_offset = input[list_open_bracket_offset + 1:].index("[") + list_open_bracket_offset + 1
        if list_open_bracket_offset >= list_close_bracket_offset:
            if "]" in input[list_close_bracket_offset + 1:]:
                list_close_bracket_offset = input[list_close_bracket_offset + 1:].index("]") + list_close_bracket_offset + 1
            else:
                return None

        out = evaluate_list_string(input, list_open_bracket_offset, list_close_bracket_offset)

    return out


"""
Given an arbitrary input string from the user, extract the list of anagram strings, and group them together


Input:
    Please group the anagrams in this list ["affx", "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]
    
Output:
    [["a"], ["ab", "ba"], ["nnx", "xnn"], ["cde", "edc", "dce"], ["xffa", "affx"]]
    
Analysis:
    Runtime: O(n + n) = O(n)
        - extract anagram list from string : O(n)
        - for each word in anagram list, loop through each character : O(n)
            - dictionary lookup is constant time
    Space: O(n + n) = O(n)
        - extract anagram list from string : O(n)
        - dictionary to store constant length key that represents each group of anagram : O(n)
        - the key though can grow arbitrarily if some characters can appear more than 10 times in a word
"""
def group_anagrams(input : str) -> Optional[List[List[str]]]:
    anagram_list : List[str] = extract_anagram_list_from_input(input)
    
    if anagram_list:
        table = {}
        for word in anagram_list:
            key = ["0"] * 26
            for char in word:
                key[ord(char)-97] = str(int(key[ord(char)-97]) + 1)

            key_str = "".join(key)
            if key_str in table:
                table[key_str].append(word)
            else:
                table[key_str] = [word]
        return list(table.values())

    return None
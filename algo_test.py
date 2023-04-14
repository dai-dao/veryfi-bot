import unittest
from algo import extract_anagram_list_from_input, group_anagrams
from typing import List


class TestAlgo(unittest.TestCase):

    def test_good_cases_extract_anagram_list_from_input(self):
        correct_output = ['affx', 'a', 'ab', 'ba', 'nnx', 'xnn', 'cde', 'edc', 'dce', 'xffa']
        good_test_cases = [
            """Please group the [bla] anagrams in this list ["affx", "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]""",
            """Please group the anagrams in this list ["affx", "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]""",
            """Please group ] the anagrams in this list ["affx", "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]""",
            """Please group [ the anagrams in this list ["affx", "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]""",
            """Please group [ the anagrams ] in this list ["affx", "a", 'ab', "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]""",
            """Please group [just testing] the ] anagrams [ in this list ["affx", "a", "ab", 'ba', "nnx", "xnn", "cde", "edc", "dce", "xffa"]""",
            """Please group [] the ] anagrams [ in this list \n["affx", "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]""",
            """Please group [] the ] anagrams [ in this list ["affx",\n\n "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]""",
            """Please group [] the ] anagrams [ in this list [\n\n"affx", "a", 'ab', "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"\n\n]"""
        ]
        self.assertTrue(all(extract_anagram_list_from_input(case) == correct_output for case in good_test_cases))


    def test_bad_cases_extract_anagram_list_from_input(self):
        test_cases = [
            """Please group the [] anagrams in this list "affx", "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]""",
            """Please group the anagrams in this list [", "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]""",
            """Please group ] the anagrams in this list ["affx" "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]""",
            """Please group ] the anagrams in this list ["affx", "131a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]""",
            """Please group [ the anagrams in this list ["aff\nx", "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]""",
            """Please group [ the anagrams ] in this list ["aff  x", "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]""",
            """Please group the anagrams in this list ["affx", "a", "ab', "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]""",
            """Please group the anagrams in this list "affx", "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa""",
        ]
        
        for case in test_cases:
            out = extract_anagram_list_from_input(case)
            if not (out is None or out == []):
                self.assertTrue(False)


    def test_group_anagrams(self):
        def validate_grouped_anagrams(input : str, output : List[str]) -> bool:
            anagram_list : List[str] = extract_anagram_list_from_input(input)
            word_count = 0
            for sublist in output:
                word_count += len(sublist)
                sorted_word = ""
                for word in sublist:
                    if sorted_word == "":
                        sorted_word = "".join(sorted(word))
                    else:
                        if "".join(sorted(word)) != sorted_word:
                            return False 
            return len(anagram_list) == word_count
        
        test_cases = [
            """Please group the [] anagrams in this list ["affx", "a", "ab", "ba", "nnx", "xnn", "cde", "edc", "dce", "xffa"]""",
            """Group the anagrams in this list ["aaaaaaaaaaaaaaaaaaa", "bbbbbbbbbbbbbbbb", "aaaaaaaaaaaaaaaaaaa", "ba", "nnx", "bbbbbbbbbbbbbbbb", "cde", "edc", "dce", "xffa"]""",
            """Group the anagrams in this list [""]""",
        ]
        for case in test_cases:
            grouped_anagrams = group_anagrams(case)
            self.assertTrue(validate_grouped_anagrams(case, grouped_anagrams))


if __name__ == '__main__':
    unittest.main()
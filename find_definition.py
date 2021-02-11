# -*- coding: UTF-8 -*-
import os
import re

temp_list = notepad.getCurrentFilename().rsplit('.', 1)
dir_path = os.path.dirname(os.path.realpath(notepad.getCurrentFilename()))
filename_noext = ((os.path.basename(notepad.getCurrentFilename())).rsplit('.', 1))[0]
ext = temp_list[1].lower()
org_depth = len(dir_path.split('\\'))
TOTAL_DEPTH_UP = 6
TOTAL_DEPTH_DOWN = 10 + TOTAL_DEPTH_UP
killme = False
wordSelected = editor.getSelText()
# searchTerms = ["class " + wordSelected, "struct " + wordSelected, "typedef " + wordSelected]
searchTerms1 = r'((^\s*class\s+)|(^\s*struct\s+))' + wordSelected + r'(?!.*;)'
searchTerms2 = r'(^\s*typedef\s+.*\s?)' + wordSelected + r';'
## In short, to match a literal backslash, one has to write '\\\\' as the RE string, because the regular 
## expression must be \\, and each backslash must be expressed as \\ inside a regular Python string literal. 
## In REs that feature backslashes repeatedly, this leads to lots of repeated backslashes and makes the 
## resulting strings difficult to understand.
## The solution is to use Pythons raw string notation for regular expressions; backslashes are not handled 
## in any special way in a string literal prefixed with 'r', so r"\n" is a two-character string containing '\'
## and 'n', while "\n" is a one-character string containing a newline. Regular expressions will often be 
## written in Python code using this raw string notation.
## In addition, special escape sequences that are valid in regular expressions, but not valid as Python 
## string literals, now result in a DeprecationWarning and will eventually become a SyntaxError, which 
## means the sequences will be invalid if raw string notation or escaping the backslashes isn’t used.
##                                   Regular String  Raw string
##                                   "ab*"           r"ab*"
##                                   "\\\\section"   r"\\section"
##                                   "\\w+\\s+\\1"   r"\w+\s+\1"

print (dir_path)
print (filename_noext)
print (ext)
print (org_depth)

if len(temp_list) == 2:
    console.clear()
    console.writeError("STARTING SEARCH...\n")     
    console.show()
    if ext in [ 'cpp', 'c', 'h' ]:
        all_except_ext = temp_list[0]
        for root, directories, filenames in os.walk(dir_path + "\\.."*TOTAL_DEPTH_UP + "\\", topdown=True):
            filenames = [ fi for fi in filenames if fi.endswith(".h") ]
            filenames.sort()
            for filename in filenames:  
                current_file = os.path.join(root, filename)
                current_file_depth = len(current_file.split('\\'))
                if (current_file_depth-org_depth) > TOTAL_DEPTH_DOWN:
                    break
                else:
                    # print (current_file)
                        # Open the file in read only mode
                    if os.path.exists(current_file):
                        with open(current_file, 'r') as read_obj:
                            # Read all lines in the file one by one
                            for idx, line in enumerate(read_obj):
                                # For each line, check if line contains the string
                                # if any(term in line for term in searchTerms):
                                if re.search(searchTerms1, line):
                                   notepad.open(os.path.join(root, filename))
                                   editor.gotoLine(idx)
                                   killme = True
                                   console.writeError("FOUND IT!\n")     
                                   console.show()
                                   console.hide()
                                   break
                                elif re.search(searchTerms2, line):
                                   notepad.open(os.path.join(root, filename))
                                   editor.gotoLine(idx)
                                   killme = True
                                   console.writeError("FOUND IT!\n")     
                                   console.show()
                                   console.hide()
                                   break
                    else: 
                        continue
            if killme:
                break
        else:
            console.writeError("NONE FOUND!\n")     
            console.show()      
    else:
        console.clear()
        console.writeError("UNSUPPORTED FILE TYPE\n")     
        console.show()

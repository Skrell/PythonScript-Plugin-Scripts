# -*- coding: UTF-8 -*-
import os
import re
import time

console.clear()

temp_list = notepad.getCurrentFilename().rsplit('.', 1)
dir_path = os.path.dirname(os.path.abspath(notepad.getCurrentFilename()))
filename_noext = ((os.path.basename(notepad.getCurrentFilename())).rsplit('.', 1))[0]
all_except_ext = temp_list[0]
ext = temp_list[1].lower()
org_depth = len(dir_path.split('\\'))
TOTAL_DEPTH_UP = 6
TOTAL_DEPTH_DOWN = 10 + TOTAL_DEPTH_UP
killme = False
findLibraryFileToOpen = False
foundFiles = {}

wordSelected = editor.getSelText()
if wordSelected.find("(") != -1: #found a function
    wordSelected = re.sub(r"(\w+)\(", r"\1", wordSelected)
    wordSelected = wordSelected + r'\s*\('
    print wordSelected
else:
    console.writeError("NOT A FUNCTION\n")

if wordSelected.find(".h") != -1: #found an include
    findLibraryFileToOpen = True;
    wordSelected = re.sub(r"(\w+/)?(\w+)/(\w+)", r"\2\\\3", wordSelected)
    print wordSelected
    

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
print (wordSelected)

def PauseAndGo(idx):
    time.sleep(.100)
    editor.gotoLine(0)
    # editor.scrollCaret()
    # editor.gotoPos(editor.getCurrentPos())
    editor.lineScroll(0,idx - (editor.linesOnScreen()/2))
    editor.gotoLine(idx)
    return

def FindCloserPath(path1, path2):
    global org_depth
    lenPath1 = len(path1.split('\\'))
    lenPath2 = len(path2.split('\\'))
    if abs(lenPath1 - org_depth) < abs(lenPath2 - org_depth):
        # print path1, "vs", path2
        print lenPath1, "vs", lenPath2
        # print abs(lenPath1 - org_depth), "vs", abs(lenPath2 - org_depth)
        return path1
    elif abs(lenPath1 - org_depth) == abs(lenPath2 - org_depth): 
        print lenPath1, "vs", lenPath2
        return path1
    else:
        # print path1, "vs", path2
        print lenPath1, "vs", lenPath2
        # print abs(lenPath1 - org_depth), "vs", abs(lenPath2 - org_depth)
        return path2

def FoundResult(current_file, idx):
    global foundFiles
    if len(foundFiles) == 0:
        foundFiles[current_file] = os.path.basename(current_file)
        notepad.open(current_file)
    else:
        for key, value in foundFiles.items():
            if ((os.path.basename(current_file)) == value):
                new_current_file = FindCloserPath(current_file, key)
                notepad.open(new_current_file)
            else:
                foundFiles[current_file] = os.path.basename(current_file)
                notepad.open(current_file)
    
    realidx = idx + 1
    PauseAndGo(idx)
    topLine = editor.getFirstVisibleLine() + 1
    return realidx


def SearchAFile(current_file):
    global wordSelected
    global foundFiles
    result = False
    searchTerms1  = r'^\s*(?!/)((class\s+)|(struct\s+))' + r'\b' + wordSelected + r'\b(?!.*;)'
    searchTerms2  = r'^\s*(?!/)(typedef)\s+.*' + r'\b' + wordSelected + r'\b;'
    searchTerms2a = r'^\s*(?!/)(using)\s+.*' + r'\b' + wordSelected + r'\b\s+.*=.*;'
    searchTerms3  = r'^\s*(?!/)((#define\s+)|(enum\s+)|(DECLARE_SMART_ENUM\())' + r'\b' + wordSelected + r'\b(?!.*;)'
    searchTerms3a = r'^\s*(?!/)(static\s+)?const.*' + r'\b' + wordSelected + r'(?!.*\()' + r'\b.*=.*;'
    # Function Definitions
    # searchTerms4 = r'^\s*(?!/)(inline\s+)?(const\s+)?((\w+::)?\w+\s)?(\*|&)?\w+::' + wordSelected + r'.*(?!.*;)'
    searchTerms5 = r'^\s*(?!/)((\w+::)?\w+(<.*>)?\s+){1,2}(\*|&)?\s*' + r'(\w+::)?' + wordSelected + r'\s*(const\s+)?(\{.*)?(?!.*\) (override)?(= 0)?;)'    
    with open(current_file, 'r') as read_obj:
        if wordSelected.find("(") == -1 and current_file.endswith(".h"): #not a func and a header
            # Read all lines in the file one by one
            for idx, line in enumerate(read_obj):
                # For each line, check if line contains the string
                # if any(term in line for term in searchTerms):
                if re.search(searchTerms1, line):
                   realidx = FoundResult(current_file, idx)
                   result = True
                   console.writeError("FOUND SearchTerm1 IN " + current_file + " on line # " + str(realidx) + "!\n")
                   console.show()
                   break
                elif re.search(searchTerms2, line):
                   realidx = FoundResult(current_file, idx)
                   result = True
                   console.writeError("FOUND SearchTerm2 IN " + current_file + " on line # " + str(realidx) + "!\n")
                   console.show()
                   break
                elif re.search(searchTerms2a, line):
                   realidx = FoundResult(current_file, idx)
                   result = True
                   console.writeError("FOUND SearchTerm2a IN " + current_file + " on line # " + str(realidx) + "!\n")
                   console.show()
                   break
                elif re.search(searchTerms3, line):
                   realidx = FoundResult(current_file, idx)
                   result = True
                   console.writeError("FOUND SearchTerm3 IN " + current_file + " on line # " + str(realidx) + "!\n")
                   console.show()
                   break
                elif re.search(searchTerms3a, line):
                   realidx = FoundResult(current_file, idx)
                   result = True
                   console.writeError("FOUND SearchTerm3a IN " + current_file + " on line # " + str(realidx) + "!\n")
                   console.show()
                   break
        elif wordSelected.find("(") != -1:
            # Read all lines in the file one by one
            for idx, line in enumerate(read_obj):                            
                # For each line, check if line contains the string
                # if any(term in line for term in searchTerms):
                # if re.search(searchTerms4, line):
                   # notepad.open(current_file)
                   # realidx = idx + 1
                   # PauseAndGo(idx)
                   # topLine = editor.getFirstVisibleLine() + 1
                   # result = True
                   # console.writeError("FOUND searchTerms4 FUNC IN " + current_file + " on line # " + str(realidx) + "!\n")
                   # console.show()
                   # break
                if re.search(searchTerms5, line):
                   realidx = FoundResult(current_file, idx)
                   result = True
                   console.writeError("FOUND searchTerms5 FUNC IN " + current_file + " on line # " + str(realidx) + "!\n")
                   console.show()
                   break
    return result
    
def walk_error(error):
    print(error.filename)
    
if len(temp_list) == 2:
    f_names = []
    done = False
    # os.path.join(path, '') will add the trailing slash if it's not already there.
    # You can do os.path.join(path, '', '') or os.path.join(path_with_a_trailing_slash, '') 
    # and you will still only get one trailing slash.
    topDir = os.path.join(os.path.abspath(dir_path + "\\.."*TOTAL_DEPTH_UP + "\\"), '')
    print "topmost directory: ", topDir
    console.show()
    console.writeError("STARTING SEARCH...\n")     
    if ext in [ 'cpp', 'c', 'h' ]:
        if SearchAFile(os.path.abspath(notepad.getCurrentFilename())):
            done = True
        else:
            for root, directories, filenames in os.walk(topDir, topdown=True, onerror=walk_error):
                for f in list(filenames):
                    if f.endswith(".h") or f.endswith(".cpp") or f.endswith(".c") or f.endswith(".hpp"):
                        f_names.append(os.path.abspath(os.path.join(root, f)))
            # f_names =  list(dict.fromkeys(f_names))  #--remove duplicates    
            for current_file in f_names:  
                # current_file = os.path.join(root, filename)
                current_file_depth = len(current_file.split('\\'))
                # print (current_file)
                if (current_file_depth-org_depth) > TOTAL_DEPTH_DOWN:
                    continue
                elif findLibraryFileToOpen and (wordSelected in current_file):
                    notepad.open(current_file)
                    done = True
                else:
                    # Open the file in read only mode to start searching through
                    if os.path.exists(current_file):
                        if SearchAFile(current_file):
                            continue
                            # done = True
                        else: 
                            continue
                if done:
                    break
    else:
        console.clear()
        console.writeError("UNSUPPORTED FILE TYPE\n")     
console.writeError("DONE!\n")     
console.hide()
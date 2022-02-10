# -*- coding: UTF-8 -*-
import os
import re
import time
from difflib import SequenceMatcher

console.clear()

selectedLineNumber = editor.lineFromPosition(editor.getCurrentPos())
selectedLine = editor.getCurLine().strip()
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
TOTAL_RESULTS = 0
funcDef = False
lookForNamespace = False

wordSelected = editor.getSelText()
if wordSelected.find("(") != -1: #found a function
    wordSelected = re.sub(r"(\w+)\(.*", r"\1", wordSelected)
    # wordSelected = wordSelected + r'\s*\('
    funcDef = True
    print wordSelected
else:
    console.writeError("NOT A FUNCTION\n")

if wordSelected.find(".h") != -1: #found an include
    findLibraryFileToOpen = True;
    wordSelected = re.sub(r'(^#include ")?(\w+/)?(\w+)/(\w+\.h)(\")?', r'\3\\\4', wordSelected)
    print "library path is ", wordSelected
    

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
print (selectedLine)
print (wordSelected)

class Signature(object):
    def __init__(self, string = "", lineStart = 0, lineSteop = 0):
        self.string = string
        self.lineStart = lineStart
        self.lineStop = lineStop
        
def FindHighestCorrelation(codestring = "", codeStringsArray = []):
    highestMatch = 0.0
    highestIdx = 0
    
    for idx, entry in enumerate(codeStringsArray):
        similarity_ratio = SequenceMatcher(None, codeString.rstrip('\r\n'),entry.string.rstrip('\r\n')).ratio()
        if similarity_ratio > highestMatch:
            highestMatch = similarity_ratio
            highestIdx = idx
    print(highestMatch)
    print("BEST MATCH: " + codestring + " vs ")
    print("            " + codeStringsArray[highestIdx].string)
    return highestIdx

def FindMatchingBraceLine(arrayOfLines = [], currentLineNum = 0, middleOfScope = False, reverseSearch = False, braceType = '{'):
    # print(currentLineNum)
    lineIndex = currentLineNum - 1
    openBraceCount = 0
    closeBraceCount = 0
    matchingBraceLine = 0
    startLookingForMatch = False
    
    if braceType == '{':
        openBrace  = '{'
        closeBrace = '}'
    elif braceType == '(':
        openBrace  = '('
        closeBrace = ')'
    elif braceType == '[':
        openBrace  = '['
        closeBrace = ']'
    
    if middleOfScope and not reverseSearch:
        openBraceCount += 1
        startLookingForMatch = True
    elif middleOfScope and reverseSearch:
        closeBraceCount += 1
        startLookingForMatch = True
    
    while lineIndex < (len(arrayOfLines)) and not reverseSearch:
        if openBrace in arrayOfLines[lineIndex]:
            numOfInstances = arrayOfLines[lineIndex].count(openBrace)
            openBraceCount += numOfInstances
            startLookingForMatch = True
            # print (arrayOfLines[lineIndex], openBraceCount)
        if closeBrace in arrayOfLines[lineIndex]:
            numOfInstances = arrayOfLines[lineIndex].count(closeBrace)
            closeBraceCount += numOfInstances
            # print (arrayOfLines[lineIndex], closeBraceCount)
        if startLookingForMatch and (openBraceCount-closeBraceCount == 0):
            matchingBraceLine = lineIndex
            # print (matchingBraceLine + 1)
            break
        lineIndex += 1
        
    while lineIndex > 0 and reverseSearch:
        if closeBrace in arrayOfLines[lineIndex]:
            numOfInstances = arrayOfLines[lineIndex].count(closeBrace)
            closeBraceCount += numOfInstances
            startLookingForMatch = True
            # print (arrayOfLines[lineIndex].strip(), closeBraceCount)
        if openBrace in arrayOfLines[lineIndex]:
            numOfInstances = arrayOfLines[lineIndex].count(openBrace)
            openBraceCount += numOfInstances
            # print (arrayOfLines[lineIndex].strip(), openBraceCount)
        if startLookingForMatch and (openBraceCount-closeBraceCount == 0):
            matchingBraceLine = lineIndex
            # print (matchingBraceLine + 1)
            break
        lineIndex -= 1        
        
    if matchingBraceLine == 0:
        return 0
    else:
        return (matchingBraceLine + 1)

def PauseAndGo(idx):
    time.sleep(.100)
    editor.gotoLine(0)
    # editor.scrollCaret()
    # editor.gotoPos(editor.getCurrentPos())
    editor.lineScroll(0,idx - (editor.linesOnScreen()/2))
    editor.gotoLine(idx)
    return

def CheckForFoundHeader(current_file):
    global foundFiles
    if (current_file.endswith(".h")):
        accompaniedFile = current_file.rsplit('.', 1)[0] + ".cpp"
        for key, value in foundFiles.items():
            if key == accompaniedFile:
                print("CLOSING " + current_file)
                notepad.close()
                return True
    elif (current_file.endswith(".cpp")):
        accompaniedFile = current_file.rsplit('.', 1)[0] + ".h"
        for key, value in foundFiles.items():
            if key == accompaniedFile:
                print("CLOSING " + accompaniedFile)
                notepad.activateFile(key)
                notepad.close()
                return True
    return False

def GetDiffInPathLen(path1, path2):
    lenPath1 = len(path1.split('\\'))
    lenPath2 = len(path2.split('\\'))
    diff = abs(lenPath1 - lenPath2)
    return diff

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
                if (CheckForFoundHeader(current_file)):
                    return 0
            else:
                foundFiles[current_file] = os.path.basename(current_file)
                notepad.open(current_file)
                if (CheckForFoundHeader(current_file)):
                    return 0
    
    realidx = idx + 1
    PauseAndGo(idx)
    topLine = editor.getFirstVisibleLine() + 1
    return realidx


def SearchAFile(current_file, firstSearch = False):
    global wordSelected
    global foundFiles
    global TOTAL_RESULTS
    global funcDef
    global lookForNamespace
    global selectedLine
    
    result = False
    mayContinue = False
    probablyEnum = False
    if not firstSearch:
        extension = ".h"
    else:
        extension = current_file.rsplit('.', 1)[1]
        
    i = 0
        
    searchTerms1  = r'^(?!\s*/)\s*((class\s+)|(struct\s+))' + r'\b' + wordSelected + r'\b(?!.*;)'
    searchTerms2  = r'^(?!\s*/)\s*(typedef|using)\s+.*' + r'\b' + wordSelected + r'\b(\s+.*=.*)?;'
    searchTerms3  = r'^(?!\s*/)\s*((#define\s+)|(enum\s+)|(DECLARE_SMART_ENUM\())' + r'\b' + wordSelected + r'\b(?!.*;)'
    searchTerms3a = r'^(?!\s*/)\s*(static\s+)?((constexpr|const|auto|double|int|uint|float|uint8_t|uint16_t|uint32_t)\s+){1,2}\s*\*\s*' + r'(\w+::)?\b' + wordSelected + r'\b' + r'.*((\(\w+\);)|(=.*;))'
    searchTerms4  = r'^(?!\s*/)\s*\b' + wordSelected + r'\b\s+(\= \d)?.*,'
    # Function Definitions
    searchTerms5h1 = r'^(?!\s*/)\s*((\w+::)?\w+(<.*>)?\s+){1,2}(\*|&)?\s*' + r'((\w+::)|('+wordSelected+r'::))?' + wordSelected + r'\s*\([\w\s\*&,:]*(\)\s+\bconst\b)?(\boverride\b)?(\s+\{)'    
    searchTerms5h2 = r'^(?!\s*/)\s*((\w+::)?\w+(<.*>)?\s+){1,2}(\*|&)?\s*' + r'((\w+::)|('+wordSelected+r'::))?' + wordSelected + r'\s*\([\w\s\*&,:]*(\)\s+\bconst\b)?(\boverride\b)?(\s+= 0;)'    
    searchTerms5h3 = r'^(?!\s*/)\s*((\w+::)?\w+(<.*>)?\s+){0,2}(\*|&)?\s*' + r'((\w+::)|('+wordSelected+r'::))?' + wordSelected + r'\s*\([\w\s\*&,:\)]*$'    
    searchTerms5c  = r'^(?!\s*/)\s*((\w+::)?\w+(<.*>)?\s+){0,2}(\*|&)?\s*' + r'((\w+::)|('+wordSelected+r'::))?' + wordSelected + r'\s*\([\w\s\*&,:]*(\)\s+\bconst\b)?(?!.*;)'    
    
    linesArray = open(current_file, 'r').readlines()
    
    with open(current_file, 'r') as read_obj:
        if not funcDef and current_file.endswith(extension): #not a func and a header
            # Read all lines in the file one by one
            for idx, line in enumerate(read_obj):
                if (lookForNamespace and not mayContinue):
                    if (wordSelectedArray[i] != wordSelected):
                        if ((("namespace " + wordSelectedArray[i]) in line) or 
                            (("class " + wordSelectedArray[i]) in line) or
                            (("DECLARE_SMART_ENUM(" + wordSelectedArray[i]) in line)):
                            print("Found " + wordSelectedArray[i] + ", moving onto " + wordSelectedArray[i+1] + " in " + current_file)
                            i = i + 1
                        elif ("enum class " + wordSelectedArray[i]) in line:
                            probablyEnum = True
                            print("Found " + wordSelectedArray[i] + ", moving onto " + wordSelectedArray[i+1] + " in " + current_file)
                            i = i + 1                        
                    else:
                        mayContinue = True
                else:
                    mayContinue = True
                
                if (mayContinue and (line.strip() != selectedLine)):    
                    if probablyEnum and (wordSelected in line):
                       realidx = FoundResult(current_file, idx)
                       result = True
                       console.writeError("FOUND ENUM " + current_file + " on line # " + str(realidx) + "!\n")
                       console.show()
                       TOTAL_RESULTS += 1
                       break
                    if re.search(searchTerms1, line):
                       realidx = FoundResult(current_file, idx)
                       result = True
                       console.writeError("FOUND SearchTerm1 IN " + current_file + " on line # " + str(realidx) + "!\n")
                       console.show()
                       TOTAL_RESULTS += 1
                       break
                    elif re.search(searchTerms2, line):
                       realidx = FoundResult(current_file, idx)
                       result = True
                       console.writeError("FOUND SearchTerm2 IN " + current_file + " on line # " + str(realidx) + "!\n")
                       console.show()
                       TOTAL_RESULTS += 1
                       break
                    elif re.search(searchTerms3, line):
                       realidx = FoundResult(current_file, idx)
                       result = True
                       console.writeError("FOUND SearchTerm3 IN " + current_file + " on line # " + str(realidx) + "!\n")
                       console.show()
                       TOTAL_RESULTS += 1
                       break
                    elif re.search(searchTerms3a, line):
                       realidx = FoundResult(current_file, idx)
                       result = True
                       console.writeError("FOUND SearchTerm3a IN " + current_file + " on line # " + str(realidx) + "!\n")
                       console.show()
                       TOTAL_RESULTS += 1
                       break
                    elif re.search(searchTerms4, line):
                       realidx = FoundResult(current_file, idx)
                       result = True
                       console.writeError("FOUND SearchTerm4 IN " + current_file + " on line # " + str(realidx) + "!\n")
                       console.show()
                       TOTAL_RESULTS += 1
                       break
        elif funcDef:
            # Read all lines in the file one by one
            for idx, line in enumerate(read_obj):
                if (lookForNamespace and not mayContinue):
                    if (wordSelectedArray[i] != wordSelected):
                        if ((("namespace " + wordSelectedArray[i]) in line) or 
                            (("class " + wordSelectedArray[i]) in line) or
                            (("struct " + wordSelectedArray[i]) in line)):
                            print("Found " + wordSelectedArray[i] + ", moving onto " + wordSelectedArray[i+1] + " in " + current_file)
                            i = i + 1
                    else:
                        mayContinue = True
                else:
                    mayContinue = True
                    
                if (mayContinue):
                    if current_file.endswith(".h") and (re.search(searchTerms5h1, line) or re.search(searchTerms5h2, line) or re.search(searchTerms5h3, line)):
                       print("here")
                       realidx = FoundResult(current_file, idx)
                       result = True
                       console.writeError("FOUND searchTerms5h_ FUNC IN " + current_file + " on line # " + str(realidx) + "!\n")
                       console.show()
                       TOTAL_RESULTS += 1
                       break
                    elif (current_file.endswith(".cpp") or current_file.endswith(".hpp")) and re.search(searchTerms5c, line):
                       realidx = FoundResult(current_file, idx)
                       result = True
                       console.writeError("FOUND searchTerms5c FUNC IN " + current_file + " on line # " + str(realidx) + "!\n")
                       console.show()
                       TOTAL_RESULTS += 1
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
    if ext in [ 'cpp', 'c', 'h', 'hpp' ]:
        if "::" in wordSelected:
            wordSelectedArray = wordSelected.split('::')
            wordSelected = wordSelectedArray[-1]
            print("Looking for " + wordSelected)
            lookForNamespace = True
        
        if SearchAFile(os.path.abspath(notepad.getCurrentFilename()), True):
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
                        if SearchAFile(current_file, False):
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
if (TOTAL_RESULTS <= 1):
    console.hide()


#    ------------------------------------------NOTES -------------------------------------
#    Extract the file name (base name): os.path.basename()
#    Use os.path.basename() to extract the file name from the path string.
#    =======================================================================================
#    File name with extension
#    =======================================================================================
#    os.path.basename() returns the string of the file name (base name) including the extension.
#
#    filepath = './dir/subdir/filename.ext'
#    basename = os.path.basename(filepath)
#    print(basename)
#    # filename.ext
#
#    print(type(basename))
#    # <class 'str'>
#    =======================================================================================
#    File name without extension
#    =======================================================================================
#    To extract the file name without the extension, use os.path.splitext() described later.
#
#    basename_without_ext = os.path.splitext(os.path.basename(filepath))[0]
#    print(basename_without_ext)
#    # filename
#    os.path.splitext() split at the last (right) dot .. If you want to split by the first (left) dot ., use split().
#
#    Split strings in Python (delimiter, line break, regex, etc.)
#    filepath_tar_gz = './dir/subdir/filename.tar.gz'
#
#    print(os.path.splitext(os.path.basename(filepath_tar_gz))[0])
#    # filename.tar
#
#    print(os.path.basename(filepath_tar_gz).split('.', 1)[0])
#    # filename
#    =======================================================================================
#    Extract the directory name (folder name): os.path.dirname()
#    =======================================================================================
#    Use os.path.dirname() to extract the directory name (folder name) from the path string.
#
#    filepath = './dir/subdir/filename.ext'
#    dirname = os.path.dirname(filepath)
#    print(dirname)
#    # ./dir/subdir
#
#    print(type(dirname))
#    # <class 'str'>
#    =======================================================================================
#    If you want to get only the directory name directly above the file, use os.path.basename().
#    =======================================================================================
#    subdirname = os.path.basename(os.path.dirname(filepath))
#    print(subdirname)
#    # subdir
#    Get a file / dir name pair: os.path.split()
#    Use os.path.split() to get both the file name and the directory name (folder name).
#
#    os.path.split() returns a tuple of file name returned by os.path.basename() and directory name returned by os.path.dirname().
#
#    filepath = './dir/subdir/filename.ext'
#    base_dir_pair = os.path.split(filepath)
#    print(base_dir_pair)
#    # ('./dir/subdir', 'filename.ext')
#
#    print(type(base_dir_pair))
#    # <class 'tuple'>
#
#    print(os.path.split(filepath)[0] == os.path.dirname(filepath))
#    # True
#
#    print(os.path.split(filepath)[1] == os.path.basename(filepath))
#    # True

import sys
import os
import re
from difflib import SequenceMatcher

class Identifier(object):
    def __init__(self, string = "", lineStart = 0, lineStop = 0):
        self.string = string
        self.lineStart = lineStart
        self.lineStop = lineStop
        
        
def FindHighestCorrelation(codeString = "", codeStringsArray = []):
    highestMatch = 0.0
    highestIdx = 0
    
    for idx, entry in enumerate(codeStringsArray):
        similarity_ratio = SequenceMatcher(None, codeString.rstrip('\r\n'), entry.string.rstrip('\r\n')).ratio()
        if similarity_ratio > highestMatch:
            highestMatch = similarity_ratio
            highestIdx = idx
        
        print(highestMatch)
        print("BEST MATCH: " + codestring + " vs ")
        print("            " + codeStringsArray[highestIdx].string)
        
        return highestIdx
        
def FindMatchingBraceLine(arrayOfLines = [], currentLine = 0, middleOfScope = False, reverseSearch = False):
    lineIndex = currentLine - 1
    matchingBraceLine = 0
    openBraceCount = 0
    closeBraceCount = 0
    startLookingForMatch = False
    
    if middleOfScope and not reverseSearch:
        closeBraceCount += 1
        startLookingForMatch = True
    elif middleOfScope and reverseSearch:
        openBraceCount += 1
        startLookingForMatch = True
        
    while lineIndex < (len(arrayOfLines)) and not reverseSearch:
        if '{' in arrayOfLines[lineIndex] :
            numOfInstances = arrayOfLines[lineIndex].count('{')
            openBraceCount += numOfInstances
            startLookingForMatch = True
            #print (arrayOfLines[lineIndex].strip(), "open count: ", openBraceCount);
        if '}' in arrayOfLines[lineIndex]:
            numOfInstances = arrayOfLines[lineIndex].count('}')
            closeBraceCount += numOfInstances
            #print (arrayOfLines[lineIndex].strip(), "close count: ", closeBraceCount);
        if startLookingForMatch and (openBraceCount - closeBraceCount) == 0:
            matchingBraceLine = lineIndex
            #print (matchingBraceLine + 1)
            break
        else:
            lineIndex += 1
            
    while lineIndex > 0 and reverseSearch:
        if '}' in arrayOfLines[lineIndex] :
            numOfInstances = arrayOfLines[lineIndex].count('{')
            openBraceCount += numOfInstances
            startLookingForMatch = True
            #print (arrayOfLines[lineIndex].strip(), "open count: ", openBraceCount);
        if '{' in arrayOfLines[lineIndex]:
            numOfInstances = arrayOfLines[lineIndex].count('{')
            closeBraceCount += numOfInstances
            #print (arrayOfLines[lineIndex].strip(), "close count: ", closeBraceCount);
        if startLookingForMatch and (openBraceCount - closeBraceCount) == 0:
            matchingBraceLine = lineIndex
            #print (matchingBraceLine + 1)
            break
        else:
            lineIndex -= 1
            
    if matchingBraceLine == 0:
        return 0
    else:
        return matchingBraceLine + 1
        
def main(argv):

    foundFuncs1 = []
    foundFuncs2 = []
    destination = "C:\\TEMP2\\"
    
    if (len(argv) != 3):
        print("Incorrect number of parameters!")
        for a in argv:
            print(a)
        os.system("pause")
        return
        
    if not os.path.exists(destination):
        os.makedirs(destination)
        
    file1 = open(os.path.normpath(argv[1]), 'r')
    file2 = open(os.path.normpath(argv[2]), 'r')
    
    print(os.path.normpath(argv[1]))
    print(os.path.normpath(argv[2]))
    
    fileNameNoExt1 = os.path.basename(argv[1]).rsplit('.',1)[0]
    fileNameNoExt2 = os.path.basename(argv[2]).rsplit('.',1)[0]

    newFile1 = open(destination + fileNameNoExt1 + "1." + ext1, 'w')
    newFile2 = open(destination + fileNameNoExt2 + "2." + ext2, 'w')
    
    badSearchTerms = r'(\.|else|if|==|//)'
    searchConstructor = r'^(?!\s*/)\w+::~?\w+\(.*'
    searchTerms5c = r'^(?!\s*/)\s*((\w+::)?\w(<.*>)?\s+){1,2}(\*|&)?\s*' + r'(\w+::)?' + r'\w+' + r'\s*\([\w\s\*&,:]*(\)\s+\bconst\b)?(?!.*;)'
    
    linesArray1 = file1.readlines()
    linesArray2 = file2.readLines()
    
    for idx, line in enumerate(linesArray1):
        if (re.search(searchTerms5c, line) or re.search(searchConstructor, line)) and not re.search(badSearchTerms, line):
            if idx < len(linesArray1)-1:
                closeOfFunc = FindMatchingBraceLine(linesArray1, idx+1, False, False)
                foundFuncs1.append(Identifier(line, idx+1, closeOfFunc))
                # print(line.strip())
                # print(closeOfFunc)
                
    print("============================================================================")
    
    for idx, line in enumerate(linesArray2):
        if (re.search(searchTerms5c, line) or re.search(searchConstructor, line)) and not re.search(badSearchTerms, line):
            if idx < len(linesArray2)-1:
                closeOfFunc = FindMatchingBraceLine(linesArray2, idx+1, False, False)
                foundFuncs2.append(Identifier(line, idx+1, closeOfFunc))
                # print(line.strip())
                # print(closeOfFunc)
    file1.close()
    file2.close()
    
    aMatch = False
    
    newOrDeletedFuncs1 = []
    newOrDeletedFuncs2 = foundFuncs2.copy()
    
    for aFunc1 in foundFuncs1:
        aMatch = False
        for idx, aFunc2 in enumerate(newOrDeletedFuncs2):
            similarity_ratio = SequenceMatcher(None, aFunc1.string.rstrip('\r\n'), aFunc2.string.rstrip('\r\n')).ratio()
            if similarity_ratio > 0.75:
                # print("Found a match ")
                # print(aFunc1)
                # print(aFunc2)
                # print("==============")
                aMatch = True
                
                bestMatchIdx = FindHighestCorrelation(aFunc1.string.rstrip('\r\n'), newOrDeletedFuncs2)
                idx1 = aFunc1.lineStart
                while idx1 <= aFunc1.lineStop:
                    newFile1.write(linesArray1[idx1-1])
                    idx1 += 1
                newFile1.write("\n")
                newFile1.write("\n ============================================================================================ \n")
                newFile1.write(" ============================================================================================ \n")
                
                idx2 = newOrDeletedFuncs2[bestMatchIdx].lineStart
                while idx2 <= newOrDeletedFuncs2[bestMatchIdx].lineStop:
                    newFile2.write(linesArray2[idx2-1])
                    idx2 += 1
                newFile1.write("\n")
                newFile1.write("\n ============================================================================================ \n")
                newFile1.write(" ============================================================================================ \n")
                for idx, entry in enumerate(newOrDeletedFuncs2):
                    if entry.string == newOrDeletedFuncs2[bestMatchIdx].string : 
                        del newOrDeletedFuncs2[idx]
                        break
                        
                break
                
            if aMatch:
                break
                
            if not aMatch:
                newOrDeletedFuncs1.append(aFunc1)
                print("No match for " + aFunc1.string)
                
    for aFunc1 in newOrDeletedFuncs1:
        idx1 = aFunc1.lineStart
        while idx1 <= aFunc1.lineStop:
            newFile1.write(linesArray1[idx1-1])
            idx1 += 1
            newFile1.write("\n ============================================================================================ \n")
            newFile1.write(" ============================================================================================ \n")
            
    for aFunc2 in newOrDeletedFuncs2:
        idx2 = aFunc2.lineStart
        while idx1 <= aFunc2.lineStop:
            newFile1.write(linesArray2[idx2-1])
            idx2 += 1
            newFile1.write("\n ============================================================================================ \n")
            newFile1.write(" ============================================================================================ \n")
    
    newFile1.close()            
    newFile2.close()

    print("DONE!")
    os.startfile(destination)
    
if __name__ == "__main__":
    main(sys.argv)

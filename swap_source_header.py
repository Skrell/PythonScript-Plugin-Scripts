import os
import re
import time

temp_list = notepad.getCurrentFilename().rsplit('.', 1)
dir_path = os.path.dirname(os.path.realpath(notepad.getCurrentFilename()))
filename_noext = ((os.path.basename(notepad.getCurrentFilename())).rsplit('.', 1))[0]
ext = temp_list[1].lower()
org_depth = len(dir_path.split('\\'))
TOTAL_DEPTH_UP = 3
TOTAL_DEPTH_DOWN = 8 + TOTAL_DEPTH_UP
killme = False

wordSelected = editor.getSelText()

def SearchForFileWithBaseClass(baseClass = "none"):
    if (baseClass == "none"):
        return
    print str(baseClass).strip()
    TOTAL_DEPTH_UP = 6
    TOTAL_DEPTH_DOWN = 8 + TOTAL_DEPTH_UP
    global dir_path
    global org_depth
    searchTerms  = r'^\s*((class\s+)|(struct\s+))' + r'\b' + str(baseClass).strip() + r'\b' + r'(?!.*;)'
    for root, directories, filenames in os.walk(dir_path + "\\.."*TOTAL_DEPTH_UP + "\\", topdown=True):
        filenames = [ fi for fi in filenames if fi.endswith(".h") ]
        filenames.sort()
        for filename in filenames:  
            current_file = os.path.join(root, filename)
            current_file_depth = len(current_file.split('\\'))
            if (current_file_depth-org_depth) > TOTAL_DEPTH_DOWN:
                continue
            else:
                if os.path.exists(current_file): 
                    with open(current_file, 'r') as read_obj:
                        # Read all lines in the file one by one
                        for idx, line in enumerate(read_obj):
                            if re.search(searchTerms, line):
                                print current_file
                                return current_file
                            
def FindBaseClassName():
    searchTerms = r'^\s*(?!/)(\bclass\b|\bstruct\b)\s+\w+.*public\s+(virtual\s+)?(\w+::)?(\w+)'
    current_file = os.path.realpath(notepad.getCurrentFilename())
    with open(current_file, 'r') as read_obj:
        # Read all lines in the file one by one
        for idx, line in enumerate(read_obj):
            if re.search(searchTerms,line):
                baseClass = re.sub(searchTerms, r'\5', line)
                if baseClass:
                    return baseClass
    
def ScrollToAttributeDef():
    searchTerms = r'^\s*(?!/)(?!return)(static\s+)?(const\s+)?((\w+::){1,3})?(\w+(<.*>)?\s+)?(\w+(<.*>)?\s+)(\*|&)?\s*\b' + wordSelected + r'\b.*;'
    if (wordSelected):
        current_file = os.path.realpath(notepad.getCurrentFilename())
        print (current_file)
        if os.path.exists(current_file):
            with open(current_file, 'r') as read_obj:
                # Read all lines in the file one by one
                for idx, line in enumerate(read_obj):
                    if re.search(searchTerms, line):
                        time.sleep(.300)
                        editor.gotoLine(0)
                        editor.lineScroll(0,idx - (editor.linesOnScreen()/2))
                        editor.gotoLine(idx)
                        return True
                    # else:
                        # print "keeping looking..."
    return False

def SearchForOtherFile():
    global dir_path
    global filename_noext
    global ext
    global org_depth
    global wordSelected
    killme = False
    
    if 'c' in ext:
        for root, directories, filenames in os.walk(dir_path + "\\.."*TOTAL_DEPTH_UP + "\\", topdown=True):
            filenames.sort()
            for filename in filenames:  
                current_file = os.path.join(root, filename)
                current_file_depth = len(current_file.split('\\'))
                if (current_file_depth-org_depth) > TOTAL_DEPTH_DOWN:
                    # print ("I give up! ")
                    # print (current_file_depth-org_depth)
                    continue
                else:
                    # print (os.path.join(root, filename))
                    if filename.lower() == (filename_noext.lower()+'.h'):
                        notepad.open(os.path.join(root, filename))
                        if (ScrollToAttributeDef()):
                            killme = True
                            break
            if killme:
                return True
        # else:
            # console.writeError("NONE FOUND!")     
            # console.show()
    else: #file is a header file and hence we're looking for its cpp
        for root, directories, filenames in os.walk(dir_path + "\\.."*TOTAL_DEPTH_UP + "\\", topdown=True):
            for filename in filenames:  
                filenames.sort()
                current_file = os.path.join(root, filename)
                current_file_depth = len(current_file.split('\\'))
                if (current_file_depth-org_depth) > TOTAL_DEPTH_DOWN:
                    # print ("I give up! ")
                    # print (current_file_depth-org_depth)
                    continue
                else:
                    # print (os.path.join(root, filename))
                    if filename.lower() == (filename_noext.lower()+'.c') or (filename.lower() == filename_noext.lower()+'.cpp'):
                        notepad.open(os.path.join(root, filename))
                        killme = True
                        break
                    else:
                        continue
            if killme:
                return True
        # else:
            # console.writeError("NONE FOUND!")
            # console.show()   
    return False
    
print (dir_path)
print (filename_noext)
print (ext)
print (org_depth)
print (wordSelected)

if len(temp_list) == 2:
    console.clear()
    if ext in [ 'cpp', 'c', 'h' ]:
        all_except_ext = temp_list[0]
        if (wordSelected):
            if (ScrollToAttributeDef()):
                print "found it!"
            else:
                if 'c' in ext:
                    assoc_file = all_except_ext + '.h'
                else:
                    assoc_file = all_except_ext + '.c'
                    if not os.path.exists(assoc_file): 
                        assoc_file = all_except_ext + '.cpp'
                if os.path.exists(assoc_file): 
                    notepad.open(assoc_file)
                    if (wordSelected):
                        if (ScrollToAttributeDef()):
                            print "found it!"
                        else:
                            print "attribute not found, looking for base class def..."
                            foundFile = SearchForFileWithBaseClass(FindBaseClassName())
                            if (foundFile):
                                notepad.open(foundFile)
                                if (ScrollToAttributeDef()):
                                    print "found it!"
                                else:
                                    foundFile = SearchForFileWithBaseClass(FindBaseClassName())
                                    if (ScrollToAttributeDef()):
                                        print "found it 2 levels in!"
                            else:
                                print "can't find a file with the base class definition!"
                else:
                    if SearchForOtherFile() == False:
                        console.show()
                        print "No accompanying file found"
    else:
        console.clear()
        console.writeError("UNSUPPORTED FILE TYPE")     
        console.show()

import os

temp_list = notepad.getCurrentFilename().rsplit('.', 1)
dir_path = os.path.dirname(os.path.realpath(notepad.getCurrentFilename()))
filename_noext = ((os.path.basename(notepad.getCurrentFilename())).rsplit('.', 1))[0]
ext = temp_list[1].lower()
org_depth = len(dir_path.split('\\'))
TOTAL_DEPTH_UP = 3
TOTAL_DEPTH_DOWN = 8 + TOTAL_DEPTH_UP
killme = False

wordSelected = editor.getSelText()
searchTerms = r'^\s*(static\s+)?(const\s+)?(\w+::)?(\w+\s+)?(\*|&)?\s*\b' + wordSelected + r'\b.*;'

def ScrollToAttributeDef():
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
                        return
    return
    
print (dir_path)
print (filename_noext)
print (ext)
print (org_depth)
print (wordSelected)

if len(temp_list) == 2:
    if ext in [ 'cpp', 'c', 'h' ]:
        all_except_ext = temp_list[0]
        if 'c' in ext:
            assoc_file = all_except_ext + '.h'
        else:
            assoc_file = all_except_ext + '.c'
            if not os.path.exists(assoc_file): assoc_file = all_except_ext + '.cpp'
        if os.path.exists(assoc_file): 
            notepad.open(assoc_file)
            ScrollToAttributeDef()
        else:
            if 'c' in ext:
                assoc_file = dir_path + "\\..\\" + filename_noext + ".h"
                # print (assoc_file)
            else:
                assoc_file = dir_path + "\\..\\" + filename_noext + ".c"
                # print (assoc_file)
                if not os.path.exists(assoc_file): assoc_file = dir_path + "\\..\\" + filename_noext + ".cpp"
            if os.path.exists(assoc_file): notepad.open(assoc_file)
            else:
                if 'c' in ext:
                    for root, directories, filenames in os.walk(dir_path + "\\.."*TOTAL_DEPTH_UP + "\\", topdown=True):
                        filenames.sort()
                        for filename in filenames:  
                            current_file = os.path.join(root, filename)
                            current_file_depth = len(current_file.split('\\'))
                            if (current_file_depth-org_depth) > TOTAL_DEPTH_DOWN:
                                # print ("I give up! ")
                                # print (current_file_depth-org_depth)
                                break
                            else:
                                # print (os.path.join(root, filename))
                                if filename.lower() == (filename_noext.lower()+'.h'):
                                    notepad.open(os.path.join(root, filename))
                                    killme = True
                                    break
                                else:
                                    continue
                        if killme:
                            ScrollToAttributeDef()
                            break
                    else:
                        console.writeError("NONE FOUND!")     
                        console.show()
                else:
                    for root, directories, filenames in os.walk(dir_path + "\\.."*TOTAL_DEPTH_UP + "\\", topdown=True):
                        for filename in filenames:  
                            filenames.sort()
                            current_file = os.path.join(root, filename)
                            current_file_depth = len(current_file.split('\\'))
                            if (current_file_depth-org_depth) > TOTAL_DEPTH_DOWN:
                                # print ("I give up! ")
                                # print (current_file_depth-org_depth)
                                break
                            else:
                                # print (os.path.join(root, filename))
                                if filename.lower() == (filename_noext.lower()+'.c') or (filename.lower() == filename_noext.lower()+'.cpp'):
                                    notepad.open(os.path.join(root, filename))
                                    killme = True
                                    break
                                else:
                                    continue
                        if killme:
                            ScrollToAttributeDef()
                            break
                    else:
                        console.writeError("NONE FOUND!")
                        console.show()         
    else:
        console.clear()
        console.writeError("UNSUPPORTED FILE TYPE")     
        console.show()

import os
import time
 
current_file = os.path.realpath(notepad.getCurrentFilename())
current_line = editor.lineFromPosition(editor.getCurrentPos())

localEditStartLine = []
localEditStopLine  = []
remoteEditStopLine = []
f_localEditStartLine = 0
f_localEditStopLine  = 0
f_remoteEditStopLine = 0

print (current_file)
print (current_line)

if os.path.exists(current_file): # and current_file.endswith((".cpp",".h",".c",".vcxproj",".sln",".filters",".wrproject",".project",".defs",".wrmakefile",".txt")):
    with open(current_file, 'r') as read_obj:
            # Read all lines in the file one by one
            for idx, line in enumerate(read_obj):
                if line.startswith("<<<<<<<"):
                    localEditStartLine.append(idx)
                if line.startswith("======="):
                    localEditStopLine.append(idx)
                if line.startswith(">>>>>>>"):
                    remoteEditStopLine.append(idx)
   
    # print("start is",localEditStartLine+1)
    # print("break is",localEditStopLine+1)
    # print("stop is",remoteEditStopLine+1)
    for idx, start in enumerate(localEditStartLine):
        if (current_line <= remoteEditStopLine[idx] and current_line >= localEditStartLine[idx]):
            f_localEditStartLine = localEditStartLine[idx]
            f_localEditStopLine  = localEditStopLine[idx]
            f_remoteEditStopLine = remoteEditStopLine[idx]
    if (len(localEditStartLine) == 0 and len(localEditStopLine) == 0 and len(remoteEditStopLine) == 0):
        pass
    else:
        if current_line < f_localEditStopLine and current_line >= f_localEditStartLine:
            editor.gotoLine(f_localEditStopLine)
            lineCount = 0
            while lineCount <= (f_remoteEditStopLine-f_localEditStopLine):
                editor.lineDelete()
                print("deleted line",editor.lineFromPosition(editor.getCurrentPos()))
                lineCount+=1
                # time.sleep(.3)
            editor.gotoLine(f_localEditStartLine)
            editor.lineDelete()
            print("deleted line",editor.lineFromPosition(editor.getCurrentPos()))
        else:
            editor.gotoLine(f_remoteEditStopLine)
            while lineCount <= (f_localEditStopLine-f_localEditStartLine):
        notepad.save()
else:
    console.show()
    console.writeError("BAD FILE")
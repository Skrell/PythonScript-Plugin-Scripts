import os
import sys
import threading
import itertools
import time
import subprocess
from zipfile import ZipFile

done = False
def animate();
    global done
    done = False
    for c in itertools.cycle(['|','/','-','\\']):
        if done:
            break;
        else:
            sys.stdout.write('\rWorking... ' + c)
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write('\r      ')
    sys.stdout.flush()
    return
    
    
def main(argv):
    targetzip = os.path.normpath(argv[1])
    path_folders = targetzip.split(os.sep)
    baseDir = os.path.dirname(targetzip)
    filenameNoExt = os.path.basename(targetzip).split('.',1)[0]
    ext = os.path.basename(targetzip).split('.',1)[1]
    finalDirPath = baseDir + "\\" + filenameNoExt + "\\"
    tempDir = "C:\\TEMP\\" + filenameNoExt
    localVSBDir = "C:\\VSBs\\Boards\\" + path_folders[2] + "\\" + filenameNoExt
    copyCommand = "cmd /C xcopy /E /Y /Q " + tempDir + " " + finalDirPath
    recopyCommand = "cmd /C xcopy /E /Y /Q " + localVSBDir + " " + finalDirPath
    deleteCommandThread = "@start /b cmd /C rmdir /s /q " + tempDir
    deleteCommand = "cmd /C rmdir /s /q " + tempDir
    untarCommand = "cmd /C tar -xyzf " + targetzip + " -C " + baseDir
    numSrcFilesCommand = r'cmd /C dir /a:-d /s /b ' + tempDir + r' | find /c ":\"'
    numTgtFilesCommand = r'cmd /C dir /a:-d /s /b ' + finalDirPath + r' | find /c ":\"'
    
    global done
    doFinalCheck = False
    
    print("Zip file   is: " + targetzip)
    print("Filename   is: " + filenameNoExt)
    print("Extension  is: " + ext)
    print("Target Dir is: " + finalDirPath)
    
    if (os.path.exists(tempDir) and os.path.exists(finalDirPath)):
        if (subprocess.getoutput(numSrcFilesCommand) == subprocess.getoutput(numTgtFilesCommand)):
            print("================== VERIFIED AND DONE ========================")
            return
        else:
            os.system(deleteCommand)
        
    if os.path.exists(localVSBDir) and not (os.path.exists(finalDirPath)):
        print("Found an existing folder for this VSB under " + localVSBDir + " and will use it!")
        print("Copying files...")
        t = threading.Thread(target=animate)
        t.start()
        os.system(recopyCommand)
        done = True
        t.join()
        doFinalCheck = True
        tempDir = localVSBDir
        numSrcFilesCommand = r'cmd /C dir /a:-d /s /b ' + tempDir + r' | find /c ":\"'
        print("DONE Copying from C:\\VSBs\n")
    elif os.path.exists(targetzip) and not os.path.exists(finalDirPath):
        if (ext == "zip"):
            print("UNZIPPING... " + targetzip)
            t = threading.Thread(target=animate)
            t.start()
            with ZipFile(targetzip, 'r') as zipObj:
                zipObj.extractall("C:\\TEMP")
            done = True
            t.join()
        elif (ext == "tar.gz"):
            t = threading.Thread(target=animate)
            t.start()
            print("UNTARBALLING... " + targetzip)
            os.system(untarCommand)
            done = True
            t.join()
            
        if (os.path.exists(tempDir)):
            print("Now moving from " + tempDir + " to " + finalDirPath)
            t = threading.Thread(target=animate)
            t.start()
            os.system(copyCommand)
            done = True
            t.join()
            doFinalCheck = True
            print("DONE Unzipping and copying!")
            print("CLEANING UP!")
            os.system(deleteCommandThread)
            print("DONE CLEANING!\n")
        elif (os.path.exists(finalDirPath)):
            print("DONE Unzipping and copying!")
        else:
            print("Something went wrong and temp directory apepars to be missing...", tempDir, "\n")
    elif os.path.exists(finalDirPath):
        print("Target directory appears already present: " + finalDirPath)
    else:
        print("Not a valid file!\n")
        
    if (doFinalCheck):
        if (subprocess.getoutput(numSrcFilesCommand) == subprocess.getoutput(numTgtFilesCommand)):
            print("===================== VERIFIED AND DONE =========================")
            return
        else:
            print("XXXXXXXXXXXXXXXXXX SOMETHING WENT WRONG, PLZ TRY AGAIN XXXXXXXXXXXXXXXXXXXX")
    
    print("======================== DONE =================================")
    return
    
if __name__ == "__main__":
    main(sys.argv)
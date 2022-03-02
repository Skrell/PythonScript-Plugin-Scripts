import os
import sys
import threading
import itertools
import time
from zipfile import ZipFile

done = False

def animate():
    global done
    done = False
    for c in itertools.cycle(['|','/','-','\\']):
        if done:
            sys.stdout.flush()
            print()
            break;
        else:
            sys.stdout.write('\rWorking... ' + c)
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write('\r      ')
    sys.stdout.flush()
    return
    
def getNumberOfFiles(targetDir = ""):
    total = 0
    for path, dirs, files in os.walk(targetDir):
        total += len(files)
    return total
    
def main(argv):
    if len(argv) != 2:
        print("==================INCORRECT NUMBER OF PARAMETERS==================")
        for idx, v in enumerate(argv):
            print(idx,"is",v)
        print("======================== DONE =================================")
        return
        
    targetzip = os.path.normpath(argv[1])
    path_folders = targetzip.split(os.sep)
    baseDir = os.path.dirname(targetzip)
    filenameNoExt = os.path.basename(targetzip).split('.',1)[0]
    ext = os.path.basename(targetzip).split('.',1)[1]
    finalDirPath = baseDir + "\\" + filenameNoExt + "\\"
    localVSBDir = "C:\\VSBs\\Boards\\" + path_folders[2] + "\\" + filenameNoExt
    tempDir = "C:\\Temp" + filenameNoExt
   
    copyCommand = "cmd /C xcopy /E /Y /Q " + tempDir + " " + finalDirPath
    copyCommandThread = "@start /b cmd /C xcopy /E /Y /Q " + tempDir + " " + localVSBDir
    recopyCommand = "cmd /C xcopy /E /Y /Q " + localVSBDir + " " + finalDirPath
    deleteCommandThread = "@start /b cmd /C rmdir /s /q " + tempDir
    untarCommand = "cmd /C tar -xzf " + targetzip + " -C " + baseDir
    
    global done
    doFinalCheck = False
    
    print("Zip file   is: " + targetzip)
    print("Filename   is: " + filenameNoExt)
    print("Extension  is: " + ext)
    print("Target Dir is: " + finalDirPath)
    
    if os.path.exists(finalDirPath) and getNumberOfFiles(finalDirPath) > 0:
        print("FOUND ", getNumberOfFiles(finalDirPath))
        if (getNumberOfFiles(tempDir) == getNumberOfFiles(finalDirPath)):
            print("================== VERIFIED AND DONE ========================")
            return
        elif (getNumberOfFiles(localVSBDir) == getNumberOfFiles(finalDirPath)):
            print("================== VERIFIED AND DONE ========================")
            return
        else:
            print("================== MISMATCH # OF FILES, CLEANING ========================")
            if os.path.exists(tempDir):
                os.system("cmd /C rmdir /s /q " + tempDir)
            if os.path.exists(localVSBDir):
                os.system("cmd /C rmdir /s /q " + localVSBDir)
            if os.path.exists(finalDirPath):
                os.system("cmd /C rmdir /s /q " + finalDirPath)
    
    if os.path.exists(localVSBDir) and getNumberOfFiles(localVSBDir) > 0 and not (os.path.exists(finalDirPath)):
        print("Found an existing folder for this VSB under " + localVSBDir + " and will use it!")
        print("Copying files...")
        t = threading.Thread(target=animate)
        t.start()
        os.system(recopyCommand)
        done = True
        t.join()
        doFinalCheck = True
        tempDir = localVSBDir
        print("DONE Copying from C:\\VSBs\n")
    elif os.path.exists(targetzip) and (os.path.exists(finalDirPath) == False or getNumberOfFiles(finalDirPath) == 0):
        if (ext == "zip"):
            print("\nUNZIPPING... " + targetzip)
            t = threading.Thread(target=animate)
            t.start()
            with ZipFile(targetzip, 'r') as zipObj:
                zipObj.extractall("C:\\TEMP")
            done = True
            t.join()
        elif (ext == "tar.gz"):
            t = threading.Thread(target=animate)
            t.start()
            print("\nUNTARBALLING... " + targetzip)
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
            os.system(copyCommandThread)
            print("DONE CLEANING!\n")
        elif (os.path.exists(finalDirPath)):
            print("DONE Unzipping and copying!")
        else:
            print("Something went wrong and temp directory apepars to be missing...", tempDir, "\n")
    elif os.path.exists(finalDirPath):
        print("Target directory appears already present and contains files: " + finalDirPath)
    else:
        print("Not a valid file!\n")
        
    if (doFinalCheck):
        if (getNumberOfFiles(tempDir) > 0 and getNumberOfFiles(tempDir) == getNumberOfFiles(finalDirPath)):
            print("===================== VERIFIED AND DONE =========================")
            return
        else:
            print("XXXXXXXXXXXXXXXXXX SOMETHING WENT WRONG, PLZ TRY AGAIN XXXXXXXXXXXXXXXXXXXX")
    
    print("======================== DONE =================================")
    return
    
if __name__ == "__main__":
    main(sys.argv)

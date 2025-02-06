from auxFunctions import *
import json
from PIL import Image
import sys

piexifCodecs = [k.casefold() for k in ['TIF', 'TIFF', 'JPEG', 'JPG']]
piexifCodecsToConvert = [k.casefold() for k in ['TIF', 'TIFF']]
piexifCodecsToRename = [k.casefold() for k in ['JPEG']]
videoCodecs = [k.casefold() for k in ['MP4', 'MOV']]
    
def mainProcess(browserPath, editedW, convertAll, convertIfNeeded):    
    mediaMoved = []  # array with names of all the media already matched
    path = browserPath  # source path
    fixedMediaPath = path + "/MatchedMedia"  # destination path
    nonEditedMediaPath = path + "/EditedRaw"
    errorCounter = 0
    successCounter = 0
    editedWord = editedW or "edited"
    convertAll = convertAll or False
    convertIfNeeded = convertIfNeeded or True
    print(editedWord)

    try:
        obj = list(os.scandir(path))  #Convert iterator into a list to sort it
        obj.sort(key=lambda s: len(s.name)) #Sort by length to avoid name(1).jpg be processed before name.jpg
        createFolders(fixedMediaPath, nonEditedMediaPath)
    except Exception as e:
        print("Error: Choose a valid directory: " + path)
        return

    for entry in obj:
        if entry.is_file() and entry.name.endswith(".json"):  # Check if file is a JSON
            with open(entry, encoding="utf8") as f:  # Load JSON into a var
                data = json.load(f)

            progress = round(obj.index(entry)/len(obj)*100, 2)
            print(str(progress) + "%")

            #SEARCH MEDIA ASSOCIATED TO JSON

            titleOriginal = data['title']  # Store metadata into vars

            try:
                result = searchMedia(path, titleOriginal, mediaMoved, nonEditedMediaPath, editedWord)
                title = result[0]
                movedTitle = result[1]
                movedFilePath = result[2]

            except Exception as e:
                print("Error on searchMedia() with file " + titleOriginal)
                errorCounter += 1
                continue

            filepath = path + "/" + title
            if title == "None":
                print("Error: " + titleOriginal + " not found")
                errorCounter += 1
                continue
            
            # TARGET MEDIA METADATA EDIT
            filepath = updateFileMetadata(data, filepath, title, convertIfNeeded)
            if filepath is None:
                errorCounter += 1
                continue
            
            #MOVE FILE AND DELETE JSON
            os.replace(filepath, fixedMediaPath + "/" + title)
            os.remove(path + "/" + entry.name)
            mediaMoved.append(title)
            successCounter += 1
            
            # ORIGINAL MEDIA METADATA EDIT (IF ANY) 
            if not movedFilePath == "None" and not movedTitle == "None":
                if updateFileMetadata(data, movedFilePath, movedTitle, convertIfNeeded) is None:
                    errorCounter += 1
                else:
                    successCounter += 1
                    mediaMoved.append(movedTitle)
            
            # RELATED VIDEO METADATA EDIT (IN CASE OF HEIC)
            filePathName = filepath.rsplit('.', 1)[0]
            fileName = title.rsplit('.', 1)[0].casefold()
            fileExtension = title.rsplit('.', 1)[1].casefold()        
            if fileExtension == "heic".casefold():
                # in case of HEIC (Apple iOS dynamic photos) update related MP4 metadata as well
                mp4FilePath = filePathName + ".MP4"
                mp4Title = fileName + ".MP4"
                if os.path.exists(mp4FilePath):
                    if updateFileMetadata(data, mp4FilePath, mp4Title, False) is None:
                        errorCounter += 1
                    else:
                        os.replace(mp4FilePath, fixedMediaPath + "/" + mp4Title)
                        successCounter += 1

            
    sucessMessage = " successes"
    errorMessage = " errors"

    #UPDATE INTERFACE
    if successCounter == 1:
        sucessMessage = " success"

    if errorCounter == 1:
        errorMessage = " error"

    print(100)
    print("Matching process finished with " + str(successCounter) + sucessMessage + " and " + str(errorCounter) + errorMessage + ".")


def updateFileMetadata(data, filepath, title, convertIfNeeded):
    # METADATA EDIT
    timeStamp = int(data['photoTakenTime']['timestamp'])  # Get creation time
    print(filepath)
    
    filePathName = filepath.rsplit('.', 1)[0]
    fileExtension = title.rsplit('.', 1)[1].casefold()        
            
    if fileExtension in piexifCodecs:  # If PIEXIF is supported (images only)
        # Convert/rename to jpg
        converted = False
        if convertAll or fileExtension in piexifCodecsToConvert:
            filepath = convertToJpg(filepath, filePathName, title)
            converted = True
        elif fileExtension in piexifCodecsToRename:
            filepath = renameToJpg(filepath, filePathName, title)
        
        if filepath is None:
            # Error converting/renaming to jpg
            return None
        
        error = set_Images_EXIF_Managed(filepath, data['geoData']['latitude'], data['geoData']['longitude'], data['geoData']['altitude'], timeStamp)
        
        # If failed for not a JPEG error, try to convert to JPG (if it wasn't done before)
        if convertIfNeeded and not error is None and not converted and str(error).casefold() == "Given data isn't JPEG.".casefold():
            filepath = convertToJpg(filepath, filePathName, title)
            if filepath is None:
                # Error converting/renaming to jpg
                return None
                
            # Retry set_EXIF with converted file
            error = set_Images_EXIF_Managed(filepath, data['geoData']['latitude'], data['geoData']['longitude'], data['geoData']['altitude'], timeStamp)
        
        # Error handler
        if not error is None:
            print("Error: Inexistent EXIF data for " + filepath)
            print(str(error))
            return None
    
    if fileExtension in videoCodecs:  # If Video Codec is detected try to set gps exif with exiftool if needed
        set_QuickTime_Video_EXIF(filepath, data['geoData']['latitude'], data['geoData']['longitude'], data['geoData']['altitude'])
    
    setFileTime(filepath, timeStamp) #File creation and modification time
    
    return filepath


def set_Images_EXIF_Managed(filepath, lat, lng, altitude, timeStamp):
    try:
        set_Images_EXIF(filepath, lat, lng, altitude, timeStamp)
        return None
    except Exception as e:  # Error handler        
        return e


def convertToJpg(filepath, filePathName, title):
    try:
        # Open and convert img to jpg
        im = Image.open(filepath)
        
        # Rename to jpg
        filepath = renameToJpg(filepath, filePathName, title)
        if filepath is None:
            # Error renaming to jpg
            return None
        
        # Save img
        im.save(filepath, format='jpeg', exif=im.getexif())
        
        #rgb_im = im.convert('RGB')
        #rgb_im.save(filepath)
        
        return filepath
    except ValueError as e:
        print("Error converting to JPG in " + title)
        return None

def renameToJpg(filepath, filePathName, title):
    try:
        # Rename img to jpg
        os.replace(filepath, filePathName + ".jpg")
        filepath = filePathName + ".jpg"
        return filepath
    except ValueError as e:
        print("Error renaming to JPG in " + title)
        return None



## App initialization

if len(sys.argv) > 1:
    folder = sys.argv[1]
    
    editedW = sys.argv[2] if len(sys.argv) > 2 else None

    convertAll = None
    if len(sys.argv) > 3:
        if sys.argv[3].casefold() == "true".casefold():
            convertAll = True
        elif sys.argv[3].casefold() == "false".casefold():
            convertAll = False
    
    convertIfNeeded = None
    if len(sys.argv) > 4:
        if sys.argv[4].casefold() == "true".casefold():
            convertIfNeeded = True
        elif sys.argv[4].casefold() == "false".casefold():
            convertIfNeeded = False
        
    mainProcess(folder, editedW, convertAll, convertIfNeeded)

import os
import glob
import time
from datetime import datetime
import piexif
from fractions import Fraction
from exiftool import ExifToolHelper

et=ExifToolHelper()

# Function to search media associated to the JSON
def searchMedia(path, title, mediaMoved, nonEdited, editedWord):    
    title = fixTitle(title)
    getOriginalFilePath = lambda fileName : path + "/" + fileName
    getNonEditedFilePath = lambda fileName : nonEdited + "/" + fileName
    
    realTitle = str(title.rsplit('.', 1)[0] + "-" + editedWord + "." + title.rsplit('.', 1)[1])
    movedTitle = None
    movedFilePath = None
    filepath = path + "/" + realTitle  # First we check if exists an edited version of the image
    if not os.path.exists(filepath):
        realTitle = str(title.rsplit('.', 1)[0] + "(1)." + title.rsplit('.', 1)[1])
        filepath = path + "/" + realTitle  # First we check if exists an edited version of the image
        if not os.path.exists(filepath) or len(glob.glob(path + "/" + title + "*(1).json")) > 0:
            realTitle = title
            filepath = path + "/" + realTitle  # If not, check if exists the path with the same name
            if not os.path.exists(filepath):
                realTitle = checkIfSameName(title, title, mediaMoved, 1)  # If not, check if exists the path to the same name adding (1), (2), etc
                filepath = str(path + "/" + realTitle)
                if not os.path.exists(filepath):
                    title = (title.rsplit('.', 1)[0])[:47] + "." + title.rsplit('.', 1)[1]  # Sometimes title is limited to 47 characters, check also that
                    realTitle = str(title.rsplit('.', 1)[0] + "-" + editedWord + "." + title.rsplit('.', 1)[1])
                    filepath = path + "/" + realTitle
                    if not os.path.exists(filepath):
                        realTitle = str(title.rsplit('.', 1)[0] + "(1)." + title.rsplit('.', 1)[1])
                        filepath = path + "/" + realTitle
                        if not os.path.exists(filepath) or len(glob.glob(path + "/" + title + "*(1).json")) > 0: # os.path.exists(path + "/" + title + "(1).json"):
                            realTitle = title
                            filepath = path + "/" + realTitle
                            if not os.path.exists(filepath):
                                realTitle = checkIfSameName(title, title, mediaMoved, 1)
                                filepath = path + "/" + realTitle
                                if not os.path.exists(filepath):  # If path not found, return null
                                    realTitle = None
                        else:
                            # Move original media to another folder
                            movedTitle = title
                            movedFilePath = getNonEditedFilePath(title)
                            os.replace(getOriginalFilePath(title), movedFilePath)
                    else:
                        # Move original media to another folder
                        movedTitle = title
                        movedFilePath = getNonEditedFilePath(title)
                        os.replace(getOriginalFilePath(title), movedFilePath)
        else:
            # Move original media to another folder
            movedTitle = title
            movedFilePath = getNonEditedFilePath(title)
            os.replace(getOriginalFilePath(title), movedFilePath)
    else:
        # Move original media to another folder
        movedTitle = title
        movedFilePath = getNonEditedFilePath(title)
        os.replace(getOriginalFilePath(title), movedFilePath)

    return [str(realTitle), str(movedTitle), str(movedFilePath)]

# Supress incompatible characters
def fixTitle(title):
    return str(title).replace("%", "").replace("<", "").replace(">", "").replace("=", "").replace(":", "").replace("?","").replace(
        "¿", "").replace("*", "").replace("#", "").replace("&", "").replace("{", "").replace("}", "").replace("/", "").replace(
        "@", "").replace("!", "").replace("¿", "").replace("+", "").replace("|", "").replace("\"", "").replace("\'", "")

# Recursive function to search name if its repeated
def checkIfSameName(title, titleFixed, mediaMoved, recursionTime):
    if titleFixed in mediaMoved:
        titleFixed = title.rsplit('.', 1)[0] + "(" + str(recursionTime) + ")" + "." + title.rsplit('.', 1)[1]
        return checkIfSameName(title, titleFixed, mediaMoved, recursionTime + 1)
    else:
        return titleFixed

def createFolders(fixed, nonEdited):
    if not os.path.exists(fixed):
        os.mkdir(fixed)

    if not os.path.exists(nonEdited):
        os.mkdir(nonEdited)

def setFileTime(filepath, timeStamp):
    date = datetime.fromtimestamp(timeStamp)
    modTime = time.mktime(date.timetuple())
    os.utime(filepath, (modTime, modTime))  # Set windows file modification time

def to_deg(value, loc):
    """convert decimal coordinates into degrees, munutes and seconds tuple
    Keyword arguments: value is float gps-value, loc is direction list ["S", "N"] or ["W", "E"]
    return: tuple like (25, 13, 48.343 ,'N')
    """
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg = int(abs_value)
    t1 = (abs_value - deg) * 60
    min = int(t1)
    sec = round((t1 - min) * 60, 5)
    return (deg, min, sec, loc_value)

def change_to_rational(number):
    """convert a number to rational
    Keyword arguments: number
    return: tuple like (1, 2), (numerator, denominator)
    """
    f = Fraction(str(number))
    return (f.numerator, f.denominator)

def set_Images_EXIF(filepath, lat, lng, altitude, timeStamp):
    exif_dict = piexif.load(filepath)

    dateTime = datetime.fromtimestamp(timeStamp).strftime("%Y:%m:%d %H:%M:%S")  # Create date object
    exif_dict['0th'][piexif.ImageIFD.DateTime] = dateTime
    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = dateTime
    exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = dateTime

    exif_dict = fixExif(exif_dict)
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, filepath)
    
    print("Image Exif updated")
    
    try:
        exif_dict = piexif.load(filepath)
        
        if is_New_GPS_Valid(altitude, lat, lng) and is_Existing_Image_GPS_Tag_Inconsistent(exif_dict['GPS']):
            lat_deg = to_deg(lat, ["S", "N"])
            lng_deg = to_deg(lng, ["W", "E"])

            exiv_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
            exiv_lng = (change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2]))
            
            gps_ifd = {}
            action = "added"
            if(not exif_dict['GPS'] is None):
                gps_ifd = exif_dict['GPS']
                action = "updated"
            
            updated = []
            
            # Version
            if not has_Property_Dict(gps_ifd, piexif.GPSIFD.GPSVersionID):
                gps_ifd[piexif.GPSIFD.GPSVersionID] = (2, 0, 0, 0)
                updated.append("version")
             
            # Altitude (only added if it has some non zero value or if there is no other gps value at all)
            if abs(altitude) > 0 or \
                (not has_Property_Dict(gps_ifd, piexif.GPSIFD.GPSLatitude) and \
                    not has_Property_Dict(gps_ifd, piexif.GPSIFD.GPSLongitude)):
                if not has_Property_Dict(gps_ifd, piexif.GPSIFD.GPSAltitudeRef) or \
                    not has_Property_Dict(gps_ifd, piexif.GPSIFD.GPSAltitude):
                    gps_ifd[piexif.GPSIFD.GPSAltitudeRef] = 0 if altitude >= 0 else 1
                    gps_ifd[piexif.GPSIFD.GPSAltitude] = change_to_rational(round(altitude, 2))
                    updated.append("altitude")
                        
            # Latitude
            if not has_Property_Dict(gps_ifd, piexif.GPSIFD.GPSLatitudeRef) or \
                not has_Property_Dict(gps_ifd, piexif.GPSIFD.GPSLatitude):
                gps_ifd[piexif.GPSIFD.GPSLatitudeRef] = lat_deg[3]
                gps_ifd[piexif.GPSIFD.GPSLatitude] = exiv_lat
                updated.append("latitude")
            
            # Longitude
            if not has_Property_Dict(gps_ifd, piexif.GPSIFD.GPSLongitudeRef) or \
                not has_Property_Dict(gps_ifd, piexif.GPSIFD.GPSLongitude):
                gps_ifd[piexif.GPSIFD.GPSLongitudeRef] = lng_deg[3]
                gps_ifd[piexif.GPSIFD.GPSLongitude] = exiv_lng
                updated.append("longitude")
            
            # gps_ifd = {
            #     piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
            #     piexif.GPSIFD.GPSAltitudeRef: 1,
            #     piexif.GPSIFD.GPSAltitude: change_to_rational(round(altitude, 2)),
            #     piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
            #     piexif.GPSIFD.GPSLatitude: exiv_lat,
            #     piexif.GPSIFD.GPSLongitudeRef: lng_deg[3],
            #     piexif.GPSIFD.GPSLongitude: exiv_lng,
            # }

            exif_dict['GPS'] = gps_ifd
            
            exif_dict = fixExif(exif_dict)
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, filepath)
            
            if len(updated) > 0:
                print("Image GPS Data " + action + " for: " + filepath + " (" + ", ".join(updated) + ")")        
    except Exception as e:
        print("Warning: Image coordinates not settled")
        pass    


def set_QuickTime_Video_EXIF(filepath, lat, lng, altitude):
    try:
        updates = []
        
        # Update Video GPS Exif Data (Android encoding) if missing
        videoMetadata = get_Video_GPS_Tag(filepath, "ItemList")
        if is_New_GPS_Valid(altitude, lat, lng) and is_Existing_Video_GPS_Tag_Inconsistent(videoMetadata):
            set_Video_GPS_Tag(filepath, "ItemList", lat, lng, altitude)
            updates.append('Android')

        # Update Video GPS Exif Data (Apple encoding) if missing
        videoMetadata = get_Video_GPS_Tag(filepath, "Keys")
        if is_New_GPS_Valid(altitude, lat, lng) and is_Existing_Video_GPS_Tag_Inconsistent(videoMetadata):
            set_Video_GPS_Tag(filepath, "Keys", lat, lng, altitude)
            updates.append('Apple')
                                    
        if len(updates) > 0:
            print("Video Exif updated (" + ", ".join(updates) + ")")
    except Exception as e:
        print("Warning: Video coordinates not settled")

def get_Video_GPS_Tag(filepath, tag):
    return et.get_tags(
        [filepath],
        tags={"QuickTime:" + tag + ":GPSCoordinates"},
        params=["-g0:1"]
    )

def set_Video_GPS_Tag(filepath, tag, lat, lng, altitude):
    et.set_tags(
        [filepath],
        tags={"QuickTime:" + tag + ":GPSCoordinates": str(lat) + " " + str(lng) + " " + str(altitude)},
        params=["-overwrite_original"]
    )

def is_New_GPS_Valid(altitude, lat, lng):
    return not (altitude == 0 and lat == 0 and lng == 0)

def is_Existing_Image_GPS_Tag_Inconsistent(gpsDict):
    return gpsDict is None or len(gpsDict) == 0 \
        or not piexif.GPSIFD.GPSAltitudeRef in gpsDict or gpsDict[piexif.GPSIFD.GPSAltitudeRef] is None \
            or not piexif.GPSIFD.GPSLatitudeRef in gpsDict or gpsDict[piexif.GPSIFD.GPSLatitudeRef] is None \
                or not piexif.GPSIFD.GPSLongitudeRef in gpsDict or gpsDict[piexif.GPSIFD.GPSLongitudeRef] is None \
                or not piexif.GPSIFD.GPSAltitude in gpsDict or gpsDict[piexif.GPSIFD.GPSAltitude] is None or len(gpsDict[piexif.GPSIFD.GPSAltitude]) == 0 \
                    or not piexif.GPSIFD.GPSLatitude in gpsDict or gpsDict[piexif.GPSIFD.GPSLatitude] is None or len(gpsDict[piexif.GPSIFD.GPSLatitude]) == 0 \
                        or not piexif.GPSIFD.GPSLongitude in gpsDict or gpsDict[piexif.GPSIFD.GPSLongitude] is None or len(gpsDict[piexif.GPSIFD.GPSLongitude]) == 0

def is_Existing_Video_GPS_Tag_Inconsistent(videoExifDict):
    return not (videoExifDict and len(videoExifDict) > 0 and \
            'QuickTime:GPSCoordinates' in videoExifDict[0] and videoExifDict[0]['QuickTime:GPSCoordinates'])


def has_Property_Dict(dict, key):
    if key in dict and not dict[key] is None:
        return len(dict[key]) > 0 if type(dict[key]) == tuple else True
    return False

def fixExif(exif):
    fixesDone = []
    fixExifTuple(exif, 37121, fixesDone)
    fixExifTuple(exif, 37500, fixesDone)
    fixExifInt(exif, 41728, fixesDone)
    fixExifInt(exif, 41729, fixesDone)
    
    if len(fixesDone) > 0:
        print("Warning: Fixed Exif (" + ", ".join(fixesDone) + ")")
        
    return exif

def fixExifTuple(exif, key, fixesDone):
    # fix key_xxx should not be a tuple error (37121, 37500, etc.)
    fixed = False
    cc = exif['Exif'].get(key)
    if isinstance(cc, tuple):
        fixed = True
        exif['Exif'][key] = ",".join([str(v) for v in cc]).encode("ASCII")
    
    if fixed:
        fixesDone.append(str(key))

def fixExifInt(exif, key, fixesDone):
    # fix key_xxx should not be an int error (41728, etc.)
    fixed = False
    cc = exif['Exif'].get(key)
    if isinstance(cc, int):
        fixed = True
        exif['Exif'][key] = str(cc).encode()
    
    if fixed:
        fixesDone.append(str(key))


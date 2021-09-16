import os
import ftplib
import datetime, calendar, time
FTP_ADDR = "si.multichoice.co.za"
USERNAME = "MCA_SI_NG"
PASSWORD = "1234gnisacm!@#$"
DST_FOLDER = "/MCA-SI/StreamImages/"


def chdir(session, dirpath):
    """Change to directory."""
    if directory_exists(session, dirpath) is False: # (or negate, whatever you prefer for readability)
        print("Creating folder %s..." % dirpath)
        session.mkd(dirpath)
    print("Changing to directory %s..." % dirpath)
    session.cwd(dirpath)


def directory_exists(session, dirpath):
    """Check if remote directory exists."""
    filelist = []
    session.retrlines('LIST',filelist.append)
    for f in filelist:
        if f.split()[-1] == dirpath and f.upper().startswith('D'):
            return True
    return False

def transferFile(SRC_FILEPATH,DST_FILENAME):
    """Transfer file to FTP."""

    # Connect
    print("Connecting to FTP...")
    session = ftplib.FTP(FTP_ADDR, USERNAME, PASSWORD)


    # Change to target dir
    chdir(session, dirpath=DST_FOLDER)

    # Transfer file
    print("Transferring %s and storing as %s..." % (os.path.basename(SRC_FILEPATH), DST_FILENAME))
    with open(SRC_FILEPATH, "rb") as file:
        session.storbinary('STOR %s' % os.path.basename(DST_FILENAME), file)

    print("Closing session.")
    # Close session
    session.quit()

def extract_commandlist( filename ):
    try:
        with open(filename) as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        print(content)
        return content
    except IOError as e:
        print("Could not read file:{0.filename}".format(e))
        return []
    except: #handle other exceptions such as attribute errors
        print("Unexpected error:{}".format(e))
        return []
    

def extract_recipe_name( filename , error_list):
    try:
        recipe_list = []
        count = 0;
        error_list_len = len(error_list)
        with open(filename , 'r') as f:
            while True:
                recipe_name = ''
                line = f.readline()
                if not line:
                    break
                if -1 != line.find(':'):
                    recipe_name = line.split(':')[0]
                if len(recipe_name) != 0 :
                    #print(recipe_name)
                    for recipe in error_list:
                        if True == recipe.startswith(recipe_name):
                            recipe_list.append(recipe_name)
                            count = count + 1
                            break
                if count >= error_list_len:
                    break;
        return recipe_list
    except IOError as e:
        print("Could not read file:{0.filename}".format(e))
        return []
    except: #handle other exceptions such as attribute errors
        print("Unexpected error:{}".format(e))
        return []


def append_timestamp(filename):
    timestamp = calendar.timegm(time.gmtime())
    human_readable = datetime.datetime.fromtimestamp(timestamp).isoformat()
    filename_with_timestamp = filename + "_" + str(human_readable)
    return filename_with_timestamp


# Tool to build streama project reading commands from file and copy to ftp once completed and notify user over mail
from utils import *
import os, sys, getopt, re
import logging
# To test /home/si-vm/poky/poky/build/tmp/log/cooker/qemux86-64/console-latest.log
bitbake_str = "bitbake"
cleanall_str = " -c cleanall"
tmpfile = "handle_errors.sh"
recipe_file = "recipes.txt"
source_cmd = ''
logger = ''
log_file="log_file"

def tail(f, window=1):
    """
    Returns the last `window` lines of file `f` as a list of bytes.
    """
    if window == 0:
        return b''
    BUFSIZE = 1024
    f.seek(0, 2)
    end = f.tell()
    nlines = window + 1
    data = []
    while nlines > 0 and end > 0:
        i = max(0, end - BUFSIZE)
        nread = min(end, BUFSIZE)

        f.seek(i)
        chunk = f.read(nread)
        data.append(chunk)
        nlines -= chunk.count(b'\n')
        end -= nread
    return b'\n'.join(b''.join(reversed(data)).splitlines()[-window:])

def handle_knowerror(filename,recipe_filename):
    global logger
    status = 0

    logger.info("handle_knowerror: Reading the file to grab the errors File: " + filename )

    #Read last 100 lines for error lookup
    with open(filename, 'rb') as f:
        last_lines = tail(f, 100).decode('utf-8')
    logger.info("handle_knowerror: " + last_lines )

    #Find the errors to clean bitbake
    error_list = []
    for line in last_lines.splitlines():
        match = re.search("ERROR: Task.* failed with exit code",line)
        if match != None:
            fname = os.path.basename(line.split(" ")[2])
            error_list.append(fname.split(".")[0])


    logger.info("handle_knowerror: Error list: " + str(len(error_list)))
    logger.info(error_list)

    if len(error_list) != 0:
        list(set(error_list))
        #recipe_file_o = os.path.join(os.getcwd(), recipe_file)
        recipe_file_o = recipe_filename
        recipe_list = []
        if os.path.exists(recipe_file_o):
            recipe_list = extract_recipe_name(recipe_file_o,error_list)
        else:
            logger.info("handle_knowerror: Recipe file not exist " + recipe_file_o)

        if len(recipe_list) > 0:
            logger.info("handle_knowerror: Recipe filtering from the database")
            logger.info(recipe_list)

            #delete if file exist
            tmpfile_o = os.path.join(os.getcwd(), tmpfile)
            if os.path.exists(tmpfile_o):
                os.remove(tmpfile_o)
            logger.info("handle_knowerror: Writing the bitbake clean commands to file : " + tmpfile_o)
            os.umask(0)
            with open(os.open(tmpfile_o, os.O_CREAT | os.O_WRONLY, 0o755), "w") as f:
                #f.write(source_cmd + os.linesep)
                #f.write("source meta-rdk-mcg-hpr0a/setup-environment" + os.linesep)
                for error in recipe_list:
                    command_to_execute = ''
                    command_to_execute = bitbake_str + " " + error + cleanall_str + os.linesep
                    f.write(command_to_execute)
        else:
            status = 1
            logger.error("handle_knowerror: : No match found for the comparsion  on the recipe.txt status: "+ str(status))
    else:
        status = 1
        logger.error("handle_knowerror:No match found for the logs file :"  + filename  + "Status: " + str(status))

    if 0 == status:
        return status,tmpfile_o;
    else:
        return status,"";


def usage():
    print("Usage: ./main.py -f <filename>  -ftp <0 or 1>")
    print("     |filename    : error file to look for error")
    print("     |ftp         : 1 to upload the image to ftp, default is 0 ")
    print("     |h           : print usage")
    exit(1)

def main():
    global logger
    error_filename =''
    recipename_filename = ''
    status_code = -1
    marker = 0
    #print(len(sys.argv))
    if len(sys.argv)  < 5 :
        usage()

    opts, args = getopt.getopt(sys.argv[1:], "r:h:f:ftp:")
    for o, a in opts:
        if o == '-f':
            error_filename = a
            marker = 1
        elif o == '-ftp':
            marker = 2
        elif o == '-r':
            recipename_filename = a

    access = 0o755
    #log folder
    log_folder = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(log_folder):
        os.mkdir(log_folder, access)

    log_folder = os.path.join(log_folder, append_timestamp(log_file))
    log_folder = log_folder + ".txt"

    # Create and configure logger
    logging.basicConfig(filename= log_folder,
                        format='%(asctime)s %(message)s',
                        filemode='w')

    # Creating an object
    logger = logging.getLogger()

    # Setting the threshold of logger to DEBUG
    logger.setLevel(logging.DEBUG)
    if os.path.exists(error_filename):
        logger.info("mains: error filename:  " + error_filename + "Recipe filename: " + recipename_filename)
        status_code , command_file = handle_knowerror(error_filename,recipename_filename)
        logger.info("main:  handle_knowerror returncode: " + str(status_code) + " Filename: " + \
                    "None" if command_file=="" else command_file)
        print(command_file)
        exit(status_code)
    else:
        logger.info("handle_knowerror: Error file not found " + error_filename)

    exit(1)

if __name__ == "__main__":
    main()

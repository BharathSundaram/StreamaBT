#!/bin/bash
# Author: Bharath Shanmugasundaram Created: 02-Sep-2021
# Description: Used to automate the build and copy to FTP for Streama project

#General configuration: Can be changed based on user directory 

#./build.sh -f commands.txt -d poky/poky 2>&1 >/dev/null | tee -a stderr.out

#exec &>> your_file.log

#exec 1> >(tee x.log) 2> >(tee x.err >&2)


#All config goes for python utils and FTP Configuration
pyfile="$PWD/pythonsrc/main.py"
err_file="/tmp/log/cooker/hpr0a/console-latest.log"
recipe_file="$PWD/recipes.txt"
ftp_config="$PWD/ftp_config.cfg"
ftp_dst_folder="/MCA-SI/StreamImages/"
img_path="/tmp/deploy/images/hpr0a/install.img"

unset script_directory command_file build_directory full_command_file mark_bitbake mark_success
BASEDIR=$(dirname $0)
USER_HOME=$(eval echo ~${SUDO_USER})
BITBAKE_STR="bitbake"
#BUILD_FOLDER="build"
RETRY_COUNT=6
BUILD_FOLDER="/build-hpr0a"

#exec 3>&1 1>>logfile.txt 2>&1

ERROR_STR="Bitbake error"

function usage {
    echo "usage: build.sh [-f filename ] [-d directory ] [ -h help]"
    echo "  -f      filename which has commands to be executed"
    echo "  -d      directory to be created for the build appended to Home"
    echo "  -h      display usage"
    exit 1
}

function trapHandler
{
    retCode=$1
    echo "[$2] exited with status $retCode"
	if [ $retCode -eq 0 ]; then
		echo "$2 command was successful"
	else
		echo "$2 command failed"
		#Exit the program if it is not bitbake
		echo "Bitbake value: $3"
		if [ $3 -eq 0 ]; then	    
			exit $retCode
		fi
	fi
}


function do_init {

	if [ ! -f $1 ]; then
		echo "File not found! filename: $1"
		exit 1
	else
		# Check for build directory exist
		if [ ! -d $2 ]; then
			mkdir $2
			trapHandler $? "mkdir" 0
		else
			echo "Build folder already exist Path: $2"
			echo "Caution: Please make sure only the required commands are listed in input file (0@0)"
			echo "Do you wish to continue press 1 or 2 ?"
			select yn in "Yes" "No"; do
				case $yn in
					Yes ) break;;
					No ) exit;;
				esac
			done		
		fi			
	fi
}

handle_errors()
{
	count=0
	unset err_filename
	mark_success="OMG"
	echo "Print the current path: " $PWD

	#make the path for the error file
	err_filename=$full_build_directory$BUILD_FOLDER$err_file
	echo "Error filename: " $err_filename

	command_file=$(python3 $pyfile -f $err_filename  -r $recipe_file)
	if [ $? -eq 0 ]; then
		echo "handle_errors : command was successful: file name: $command_file"
	else
		echo "handle_errors : Command failed $?"
	exit $?
	fi
	
	#We shall retry 5 times to overcome the issue 
	
	while [ $count -lt $RETRY_COUNT ]
	do
		#Bitbake clean all commands
		echo "{^}handle_errors :Executing Bitbake clean commands: "
		bash $command_file
		trapHandler $? "Bitbake clean" 0

		echo "{^}handle_errors : Executing the command: "$1

		#echo "Sleep for 120"
		#sleep 120

		$1
		if [ $? -eq 0 ]; then
			echo "$1 handle_errors :command was successful"
			mark_success="TryFtp"			
			break
		else
			echo "$1 handle_errors : command failed"

			echo "handle_errors : Retry count: " $count
			count=`expr $count + 1`

			command_file=$(python3 $pyfile -f $err_file  -r $recipe_file)
			if [ $? -eq 0 ]; then
				echo "handle_errors : command was successful on retry: file name: $command_file"
			else
				echo "Command failed on retry $?"
			exit $?
			fi
		fi
	done

}

check_hdd_size()
{
	df -h | grep /dev/sda1

	available_size=$(df -h | grep /dev/sda1 | awk ' { print $4 } ' |  cut -d'G' -f1)
	echo $available_size

	if (( available_size <= 100 )); then
		echo "System has less that 80G: Available size: $available_size --  Aborting the build (@u@)"
		exit 1
	fi
}
# Main body starts here

echo $# arguments 
if [ "$#" -lt "4" ]; 
    then usage
	exit 0
fi

while getopts 'f:d:h:' c
do
  case $c in
    f) command_file=$OPTARG ;;
    d) build_directory=$OPTARG ;;
    h) usage exit 0 ;;
  esac
done


echo "##################### Information ################################"

echo "Command file name: $command_file Build directory: $build_directory" 
echo "Script executed from: ${PWD}"
echo "Script location: ${BASEDIR}"
echo "User home: ${USER_HOME}"
echo "Python file: $pyfile"
echo "Recipe file: $recipe_file"
echo "Ftp configfile: $ftp_config"
echo "Ftp destination folder: $ftp_dst_folder"

echo "##################### END #######################################"

script_directory=$PWD
full_command_file=$PWD/$command_file
full_build_directory=$USER_HOME/$build_directory

echo "Build path: $full_build_directory Filepath: $full_command_file"

do_init $full_command_file $full_build_directory

cd $full_build_directory

check_hdd_size

mark_bitbake=0
while read line; do
	# reading each line

	if [[ $line =~ ^[[:space:]]*#.* ]]; then
    	echo "$line starts with # so ignoring"
		continue
	fi

	if [[ "$line" =~ .*"$BITBAKE_STR".* ]]; then
		cd $full_build_directory/$BUILD_FOLDER
		trapHandler $? "cd" 0
		echo "Current direcory: " $full_build_directory/$BUILD_FOLDER
		mark_bitbake=1
	fi
	
	echo "{^}Executing the command: "$line

	$line
	res=$?
	trapHandler $res "$line" $mark_bitbake

	# We are handling the error if failed in Bitbake execution
	if [ $mark_bitbake -eq 1 ] && [ $res -ne 0 ]; then
		
		echo "*************Handle errors*************"
		handle_errors "$line"
	fi
	
	if [ $mark_bitbake -eq 1 ] && [[ "$mark_success" = "TryFtp" || $res -eq 0 ]]; then
		#Tar the file and upload
		real_img_path=$(readlink -f $full_build_directory$BUILD_FOLDER$img_path )
		filename=$(basename -- "$real_img_path")
		filename="${filename%.*}"
		echo "Image path to copy: " $real_img_path
		echo "Filename: $filename"
  
		tar -czvf "$filename.tar.gz" "$real_img_path"
		ncftpput -f $ftp_config $ftp_dst_folder "$filename.tar.gz" 
		
	fi
done < $full_command_file


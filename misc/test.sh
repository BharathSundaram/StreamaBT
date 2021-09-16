
command_file=$(python3 pythonsrc/main.py -f x.err)

if [ $? -eq 0 ]; then
	echo "command was successful: file name: $command_file"
else
	echo "Command failed $?"
    exit $?
fi

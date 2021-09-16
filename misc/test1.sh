

Handle_error()
{
	echo "True: " $1
}

mark_bitbake=1
TryFtp="TryFtp"
res=0
if [ $mark_bitbake -eq 1 ] && [[ "$TryFtp" = "TryFtp" ||  $res -eq 0 ]]; then
	echo "Testing"
else
	echo "Smiling"

fi


#test=$( Handle_error " Welcome Friend" )
Handle_error " Welcome Friend"
echo "sleep 20"

sleep 2

echo $test


command_file=$(python3 $pyfile -f $err_file  -r $recipe_file)

df -h | grep /dev/sda1

available_size=$(df -h | grep /dev/sda1 | awk ' { print $4 } ' |  cut -d'G' -f1)
echo $available_size

if (( output <= 80 )); then
	echo "System has less that 80G: Available size: $available_size -  Abort the build (@u@)"
	exit 1
fi


#/bin/bash

inotifywait -m . -e close_write -e delete |
    while read path action file; do
        #echo "The file '$file' appeared in directory '$path' via '$action'"
        # do something with the file
		#if [[ $action == "CREATE" ]] || [[ $action == "DELETE" ]] || [[ $action == "MODIFY" ]] ;then
		
		if [[ $action == "DELETE" ]] || [[ $action == "CLOSE_WRITE,CLOSE" ]] ;then
			#sleep 10
			echo "The file '$file' are $action"
			git add . && git commit -m "$(date)" && git push
			#git add . 
		fi
    done



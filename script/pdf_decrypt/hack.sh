#!/bin/bash
# 文件名因空格被分割
# 方案：修改IFS（the Internal Field Separator）
#
#
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
filelist=$(ls [!{hack}]*.pdf)

for file in $filelist
do
	# echo $file
	# suffix=${file##*.}
	name=${file%.*}
	name_pdf="hack_"${name}".pdf"
	# echo $suffix
	echo $name
	echo $name_pdf
	# name_pdf=".pdf"
	# if [ "${suffix}" = "$name_pdf" ] then
	# 	echo "succeed"
	# fi
	echo "start to trans";

	pdf2ps $file &
	pid=$!
	echo "PID:${pid} has start"
	wait ${pid}
	echo "PID:${pid} has complete"
	ps2pdf $name".ps" $name_pdf &
	pid=$!
	echo "PID:${pid} has start"
	wait ${pid}
done

IFS=$SAVEIFS
echo "$IFS" | od -t x1
IFS=$(echo -en " \n\t")
echo "$IFS" | od -t x1

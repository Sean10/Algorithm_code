# 1
tail -n +10 file.txt | head -n 1 

# 2
awk 'NR==10' file.txt 

# 4
sed -n '10p' file.txt



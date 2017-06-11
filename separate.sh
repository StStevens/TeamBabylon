#! /bin/bash


sed -i 's/,/ /g' $*
sed -i 's/Cave Spider/Cave-Spider/' $*
sed -i 's/Zombie Pigman/Zombie-Pigman/' $*

if [ ! -d sb_results ];
then
    mkdir sb_results
fi
if [ ! -d gb_results ];
then
    mkdir gb_results
fi
if [ ! -d db_results ];
then
    mkdir db_results
fi


enemies=` cat enemies.txt `

for en in $enemies;
do
    cat $1 | grep $en | awk '{print $2, $3, $4}' > sb_results/${en}.txt
    cat $2 | grep $en | awk '{print $2, $3, $4}' > gb_results/${en}.txt 
    cat $3 | grep $en | awk '{print $2, $3, $4}' > db_results/${en}.txt 
done

#!/bin/bash

head -1 output/delim.out.8100.default > output/delim.out

for file in output/delim.out.*.default ;
do
	tail -n +2 $file >> output/delim.out
done

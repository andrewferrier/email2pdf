#!/bin/bash

for filename in tests/*; do
    ./email2pdf -i $filename -o $(basename $filename).pdf
done

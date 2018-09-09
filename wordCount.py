#! /usr/bin/env python3
import string
# print ui for file names
# open file to read from
fileNameIn = input('Please enter filename ')
ff = open(fileNameIn, "r")

# open file for writing or create if it does not exists
fileNameOut = input('Enter output file name ')
f = open(fileNameOut, "w")


# create a dictionary
words = {}

#strip punctuation
for word in ff.read().split():
    cleanWord = ""
    for c in word:
        if c not in string.punctuation:
            cleanWord += c
#add word or increase count into dictionary
    if cleanWord.lower() not in words:
        words[cleanWord.lower()] = 1
    else:
        words[cleanWord.lower()] += 1

for m, n in words.items():
    f.write(str(m) + ' : ' + str(n) + '\n\n')


f.close()

print("process finished")

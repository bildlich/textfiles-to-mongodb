# This Python file uses the following encoding: utf-8

from nltk import sent_tokenize, word_tokenize, pos_tag

import os, io, re

# Settings
textFilesDirectory = "./textfiles/"
sentencesDatabase = "sentencesDatabase"
sentencesCollection = "sentencesCollection"

def processFile(pathToTextFile):
	file = io.open(pathToTextFile, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True)
	rawString = file.read().strip()

	# Basic cleaning: Replace line breaks with spaces
	def removeLineBreaks(string):
		cleanString = re.sub("[\n\r]+", " ", string)	 # Linke breaks to spaces
		cleanString = re.sub("\s{2,}", " ", cleanString) # Remove double spaces
		return cleanString

	cleanString = removeLineBreaks(rawString);

	sentences = sent_tokenize(cleanString)

	for sentence in sentences:
		print sentence
		print "---------------------"
		
	print len(sentences), 'Sentences found'
		
for filename in os.listdir(textFilesDirectory):
	print(filename + "…")
	if os.path.isfile(textFilesDirectory + filename) and filename != ".DS_Store" and filename != ".gitkeep":
		processFile(textFilesDirectory + filename)
		print("👍")
	else:
		print("❌")
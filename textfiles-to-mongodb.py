# This Python file uses the following encoding: utf-8

import re, os, random, io
import smartypants
from nltk import sent_tokenize, word_tokenize, pos_tag
from pymongo import MongoClient
from HTMLParser import HTMLParser
from complete_pairs import complete_pairs

# Settings
textFilesDirectory = "textfiles/"
sentencesDatabase = "sentencesDatabase"
sentencesCollection = "sentencesCollection"

def fileToSentenceList(pathToTextFile):
	# Import string from file
	file = io.open(pathToTextFile, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True)
	rawString = file.read().strip()

	# Basic cleaning: Replace line breaks with spaces
	def removeLineBreaks(string):
		cleanString = re.sub("[\n\r]+", " ", string)	 # Linke breaks to spaces
		cleanString = re.sub("\s{2,}", " ", cleanString) # Remove double spaces
		return cleanString

	cleanString = removeLineBreaks(rawString);
	
	# Use nltk to tokenize sentences
	# See http://www.nltk.org/api/nltk.tokenize.html#module-nltk.tokenize
	sentences = sent_tokenize(cleanString)

	# Look at all the sentences and throw out things that we don't like
	buffer = sentences
	sentences = []
	for sentence in buffer:

		# 1.
		# Throw out words that don't begin w/ capital letter (happens often after direct speech).
		# These are correct sentences but I prefer not to have them in the pool because they make little
		# sense without context.
		regex = '^[\s({\["\'“‘\-«»‹›]*[A-ZÄ-Ü0-9]'
		match = re.match(regex, sentence)
		if match is None:
			#print "thrown out b/c sentence doesn't start w/ capital letter: ", sentence
			continue

		# 2.
		# Throw out one-word or two-word sentences that contain numbers
		# They are probably headlines: 'Chapter 2.' or '1.F.1.'
		if sentence.count(" ") < 2 and re.search("\d", sentence) is not None:
			#print "thrown out b/c it seems like a nonsensical headline:", sentence
			continue

		# Remove white-space at the beginning and end
		sentence = sentence.strip()
		
		# Use typographically correct quotation marks, apostrophes and dashes
		sentence = HTMLParser().unescape(smartypants.smartypants(sentence))
		
		# Avoid unclosed (or unopened) quotation marks, parentheses, brackets, braces
		sentence = complete_pairs(sentence)

		sentences.append({
			'sentence': sentence,
			'numberOfWords': sentence.count(' ') + 1,
			'file': pathToTextFile,
			'randomPoint': [random.random(), 0] # For efficient random entry retrieval. See http://stackoverflow.com/a/9499484/836005
		})
		
	return sentences

# Iterate over all the text files in our text files directory
sentencesFromAllFiles = []
for filename in os.listdir(textFilesDirectory):
	print(filename + "…")
	if os.path.isfile(textFilesDirectory + filename) and filename != ".DS_Store" and filename != ".gitkeep":
		sentencesFromAllFiles.extend(fileToSentenceList(textFilesDirectory + filename))
		print("👍")
	else:
		print("❌")

# Connect to the database
client = MongoClient()
db = client[sentencesDatabase]
sentencesCollection = db[sentencesCollection]
# Empty the collection
sentencesCollection.remove()

# Write the sentences to the database
for index, sentence in enumerate(sentencesFromAllFiles):
	sentencesCollection.insert_one(sentence)
	
# Build collection Index for numberOfWords, random
print("Building index…")
sentencesCollection.create_index([
	("randomPoint", "2d"),
	("numberOfWords", 1)
])

counter = 0
numberOfWords = 0
for sentence in sentencesCollection.find():
	counter = counter+1
	numberOfWords += sentence['numberOfWords']

# Print a summary
print("\nSummary: There are now " + str(counter) + " sentences in the DB. On average, each sentence has " + str(numberOfWords/counter) + " words.\n")

# Print a random entry
randomInteger = random.randint(0, counter)
print("Here's a random entry:")
print(sentencesCollection.find({}).limit(-1).skip(randomInteger).next())


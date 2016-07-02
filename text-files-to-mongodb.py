# This Python file uses the following encoding: utf-8

import re, os, random

# Settings
textFilesDirectory = "textfiles/"
sentencesDatabase = "sentencesDatabase"
sentencesCollection = "sentencesCollection"

def fileToSentenceList(pathToTextFile):
	# Import string from file
	file = open(pathToTextFile, 'r')
	rawString = file.read().strip()

	# Basic cleaning: Replace line breaks with spaces
	def removeLineBreaks(string):
		cleanString = re.sub("[\n\r]+", " ", string)
		cleanString = re.sub("\s{2,}", " ", cleanString)
		return cleanString

	cleanString = removeLineBreaks(rawString);

	# Split text at common sentence delimiters
	# delimiters = "[.,!?\"…]"
	# delimiters = "\s"
	regex = ur'(?P<leftContext>[^.!?…]+)(?P<char>[.!?…]{1,3}[\'"]?)'
	regexCompiled = re.compile(regex, re.MULTILINE)
	maybeSentences = re.findall(regexCompiled, cleanString)
	if maybeSentences is None:
		print("Cannot split string into sentences.")

	# Take 3 strings and determine whether the middle string separates two sentences.
	# Inspired by http://stackoverflow.com/a/25735848/836005
	def isEndOfSentence(leftContext, char, rightContext):
		
		result = {
			'isEndOfSentence': True,
			'reasons': ["default"]
		}
		combined = leftContext + char + rightContext
	
		# 1. Not end of sentence if 1st char of rightContext isn't one of: white-space, ), ", <empty>
		match = re.match('[\s)"]', rightContext)
		if match is None and len(rightContext) > 0:
			result['isEndOfSentence'] = False
			result['reasons'].append("1st char of rightContext isnt one of white-space, ), \", <empty>")
	
		# 2. Not end of sentence if leftContext+char is in abbreviation dictionary
		# There is a catch here: If sentence ends on abbreviation ("I live in the U.S."),
		# the algorithm will not recognise the end of the sentence.
		abbrDict = [
			"Mr.", "Mrs.", "U.S.", "i.e."
		]
		str = leftContext + char
		for abbr in abbrDict:
			if str.endswith(abbr.lower()):
				result['isEndOfSentence'] = False
				result['reasons'].append("leftContext appears to end with an abbreviation: "+abbr)
	
		# 3. Not end of sentence if first char of rightContext isn't <capital letter> ,',"
		# Catch: Some english words, like 'I', are capitalized even if they are not at the
		# beginning of a sentence.
		match = re.match('[\s)"]*[A-ZÄ-Ü0-9\'"]', rightContext)
		if match is None and len(rightContext) > 0:
			result['isEndOfSentence'] = False
			result['reasons'].append("rightContext doesn't start with <capital letter>, ', \"")

		return result

	assumedSentences = [{'sentence': ''}]

	l = len(maybeSentences)
	for index, maybeSentence in enumerate(maybeSentences):
		leftContext = maybeSentence[0]
		char = maybeSentence[1]
	
		# Add the leftContext + char to the last item in our list of assumed sentences
		assumedSentences[-1]['sentence'] += leftContext + char
		
		if index == (l - 1):
			rightContext = ""
		else:
			maybeSentences[index+1]
			rightContext = maybeSentences[index+1][0]
			if isEndOfSentence(leftContext, char, rightContext)['isEndOfSentence']:
				assumedSentences.append({'sentence': ''})
			
	# Additional formatting and stuff
	for index, assumedSentence in enumerate(assumedSentences):
		# Remove white-space at the beginning and end
		assumedSentence['sentence'] = assumedSentence['sentence'].strip()
		# Make comprehensible what file the sentence was taken from
		assumedSentence['file'] = pathToTextFile
		# Overwrite the old sentence with the changes we just made
		assumedSentences[index] = assumedSentence
		# TODO: Remove lost quotation marks (trailing at the end of a sentence)
		# TODO: Consider replacing lazy quotation marks with correct quotation marks
	
	return assumedSentences

# Iterate over all the text files in our text files directory
assumedSentences = ['']
for filename in os.listdir(textFilesDirectory):
	print(filename + "…")
	if os.path.isfile(textFilesDirectory + filename) and filename != ".DS_Store":
		assumedSentences = fileToSentenceList(textFilesDirectory + filename)
		print("👍")
	else:
		print("❌")

# Connect to the database
from pymongo import MongoClient
client = MongoClient()
db = client[sentencesDatabase]
sentencesCollection = db[sentencesCollection]
# Empty the collection
sentencesCollection.remove()

# Write the sentences to the database
for index, assumedSentence in enumerate(assumedSentences):
	# Count the number of words in this sentence
	noOfWords = assumedSentence['sentence'].count(" ") + 1
	assumedSentence['noOfWords'] = noOfWords
	sentencesCollection.insert_one(assumedSentence)

counter = 0
noOfWords = 0
for sentence in sentencesCollection.find():
	counter = counter + 1
	noOfWords += sentence['noOfWords']

# Print a summary
print("\nSummary: There are now " + str(counter) + " sentences in the DB. On average, each sentence has " + str(noOfWords/counter) + " words.\n")

# Print a random entry
randomInteger = random.randint(0, counter)
print("Here's a random entry:")
print(sentencesCollection.find().limit(-1).skip(randomInteger).next())

	
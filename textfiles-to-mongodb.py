# This Python file uses the following encoding: utf-8

import re, os, random, io
import smartypants
from pymongo import MongoClient
from HTMLParser import HTMLParser
h = HTMLParser()

# Settings
textFilesDirectory = "textfiles/"
sentencesDatabase = "sentencesDatabase"
sentencesCollection = "sentencesCollection"

# This is used later to make sure acronyms are not assumed ends-of-sentences
abbrDict = [
	"Mr.", "Mrs.", "U.S.", "i.e.", "St.", "Dr."
]

# This is used later to make sure there are no lonely quotation marks in a sentence
quotationMarkDictionary = [{
	'start': '"',
	'end': '"'
	},{
	'start': '“',
	'end': '”'
	},{
	'start': '\'',
	'end': '\''
	},{
	'start': '‘',
	'end': '’'
	},{
	'start': '(',
	'end': ')'
	},{
	'start': '{',
	'end': '}'
	},{
	'start': '[',
	'end': ']'
	}]
	
# Encode the quotationMarkDictionary with UTF-8 because our text is encoded this way
for index, pair in enumerate(quotationMarkDictionary):
	quotationMarkDictionary[index] = {'start': unicode(pair['start'], "utf-8"), 'end': unicode(pair['end'], "utf-8")}

def fileToSentenceList(pathToTextFile):
	# Import string from file
	# file = open(pathToTextFile, 'r')
	file = io.open(pathToTextFile, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True)
	rawString = file.read().strip()

	# Basic cleaning: Replace line breaks with spaces
	def removeLineBreaks(string):
		cleanString = re.sub("[\n\r]+", " ", string)	 # Linke breaks to spaces
		cleanString = re.sub("\s{2,}", " ", cleanString) # Remove double spaces
		return cleanString

	cleanString = removeLineBreaks(rawString);

	# Split text at common sentence delimiters
	regex = ur'(?P<leftContext>[^.!?…]+)(?P<char>[.!?…]{1,3}[\'")]{0,2})'
	regexCompiled = re.compile(regex, re.MULTILINE)
	maybeSentences = re.findall(regexCompiled, cleanString)
	if maybeSentences is None:
		print("Cannot split string into sentences.")

	# Take 3 strings and determine whether the middle string separates two sentences.
	# Inspired by http://stackoverflow.com/a/25735848/836005
	# Leftcontext: All words before the assumed punctuation (one of .!?…)
	# char: The assumed punctuation
	# Rightcontext: All words after the assumed punctuation and before the next assumed punctuation
	
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
		str = leftContext + char
		for abbr in abbrDict:
			if str.lower().endswith(abbr.lower()):
				result['isEndOfSentence'] = False
				result['reasons'].append("leftContext appears to end with an abbreviation: "+abbr)
				
		# 3. Not the end of a sentence if leftContext ends with a roman numeral, eg XIV
		# Catch: A sentence might actually end on a roman numeral: "I read about Henry IV."
		# The algorithm will not recognise the end of this sentence.
		if len(leftContext.strip()) > 0:
			lastWord = leftContext.rsplit(None, 1)[-1]
			match = re.match('M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$', lastWord)
			if match is not None:
				result['isEndOfSentence'] = False
				result['reasons'].append("leftContext appears to end with a roman numeral: "+leftContext)

		# 4. Not end of sentence if first char of rightContext isn't <capital letter> ,',"
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

		# Use typographically correct quotation marks, apostrophes and dashes
		assumedSentence['sentence'] = HTMLParser().unescape(smartypants.smartypants(assumedSentence['sentence']))

		# If assumedSentence has quotation marks (single, double, …) and the number of opening
		# quotation marks is larger than the number of closing quotation marks, append a closing
		# quotation mark at the end of the sentence. Likewise, add opening quotation marks
		# to the beginning of the sentence if there are more closing marks than opening marks.
		for quotationMark in quotationMarkDictionary:
			numberOpenings = assumedSentence['sentence'].count(quotationMark['start'])
			numberClosings = assumedSentence['sentence'].count(quotationMark['end'])
			
			# Special case: single closing quotation marks that are not followed by white-space or the end of the sentence are assumed to be apostrophes
			if quotationMark['end'] == unicode('’', 'UTF-8'):
				numberOfApostrophes = len(re.findall(unicode('’', 'UTF-8')+'([^\s$])', assumedSentence['sentence']))
				numberClosings -= numberOfApostrophes
			
			# Are the opening and closing marks the same? ('Wrong' marks.) Then just make sure there is an even number of them
			if quotationMark['start'] is quotationMark['end'] and numberOpenings % 2 is not 0:
				# If sentence starts with this quotation mark, put the new one at the end
				if assumedSentence['sentence'].startswith(quotationMark['start']):
					assumedSentence['sentence'] += quotationMark['end']
				else:
					assumedSentence['sentence'] = quotationMark['end'] + assumedSentence['sentence']
			# Are the opening and closing marks NOT the same?
			else:
				# Are there more openings than closings? Add a mark to the end.
				if numberOpenings > numberClosings:
					assumedSentence['sentence'] += quotationMark['end']
				# Are there more closings than openings? Add a mark to the beginning
				elif numberOpenings < numberClosings:
					 assumedSentence['sentence'] = quotationMark['start'] + assumedSentence['sentence']

		# Make comprehensible what file the sentence was taken from
		assumedSentence['file'] = pathToTextFile
		# Overwrite the old sentence with the changes we just made
		assumedSentences[index] = assumedSentence

	return assumedSentences

# Iterate over all the text files in our text files directory
assumedSentences = []
for filename in os.listdir(textFilesDirectory):
	print(filename + "…")
	if os.path.isfile(textFilesDirectory + filename) and filename != ".DS_Store" and filename != ".gitkeep":
		assumedSentences.extend(fileToSentenceList(textFilesDirectory + filename))
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
print(sentencesCollection.find({}).limit(-1).skip(randomInteger).next())



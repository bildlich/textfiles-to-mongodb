# This Python file uses the following encoding: utf-8

# complete_pairs() detects 'lonely' quotation marks, parentheses, brackets, braces
# and add the missing partner. It tries to make a guess where to add this partner
# but it's not very clever: it will pick the beginning or end of the string.

# Tested on English text only.

# by Matthias Gieselmann

import re

pair_dictionary = [{
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
	
# Encode the pair_dictionary with UTF-8 because our text is encoded this way
for index, pair in enumerate(pair_dictionary):
	pair_dictionary[index] = {'start': unicode(pair['start'], "utf-8"), 'end': unicode(pair['end'], "utf-8")}

def complete_pairs(string):

	for pair in pair_dictionary:
		numberOpenings = string.count(pair['start'])
		numberClosings = string.count(pair['end'])
		
		# Special case: single closing quotation marks that are not followed by white-space or the end of the sentence are assumed to be apostrophes
		if pair['end'] == unicode('’', 'UTF-8'):
			numberOfApostrophes = len(re.findall(unicode('’', 'UTF-8')+'([^\s$])', string))
			numberClosings -= numberOfApostrophes
		
		# Are the opening and closing marks the same? ('Wrong' marks.) Then just make sure there is an even number of them
		if pair['start'] is pair['end'] and numberOpenings % 2 is not 0:
			# If sentence starts with this quotation mark, put the new one at the end
			if string.startswith(pair['start']):
				string += pair['end']
			else:
				string = pair['end'] + string
		# Are the opening and closing marks NOT the same?
		else:
			# Are there more openings than closings? Add a mark to the end.
			if numberOpenings > numberClosings:
				string += pair['end']
			# Are there more closings than openings? Add a mark to the beginning
			elif numberOpenings < numberClosings:
				 string = pair['start'] + string
	return string
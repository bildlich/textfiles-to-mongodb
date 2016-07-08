# textfiles-to-mongodb

A python script that **split a bunch of english-language text files into sentences** and puts these sentences into a MongoDB collection. A document in the collection will look like this:

    {  
      u'_id':ObjectId('5777f6947eecd42dd933589e'),
      u'numberOfWords':7,
      u'file':u'textfiles/pg1661.txt',
      u'sentence':u'“Then I do not see the point.”'
    }

![Terminal screenshot](screenshot.png?raw=true)

The hardest part, the sentence tokenization, is done with the [nltk sentence tokenizer](http://www.nltk.org/). I had written a sentence tokenizer from scratch. Then I discovered nltk and threw my work out of the window because nltk is just too good.

## Text modifications

Before inserting the sentences into the database, the following modifications are made:

* Dumb quotation marks, dashes, and apostrophes are replaced with their typographically correct counterparts.

      Before: "Then I don't see the point."
      After:  “Then I don’t see the point.”

* Unclosed (or unopened) quotation marks, parentheses, braces, and brackets are closed (resp. opened).

      Before: "Are you sure?
      After:  “Are you sure?”

* Sentences that don't start with a capital letter and other things that don't look like a sentence are thrown away

      Thrown away:     she said.
      Not thrown away: She said hello.

## Prerequisites

* [nltk](http://www.nltk.org)
* [MongoDB](https://docs.mongodb.com/manual/installation/)
* [PyMongo](https://api.mongodb.com/python/current/tutorial.html)
* [smartypants](https://pypi.python.org/pypi/smartypants)
* [smartypants](https://pypi.python.org/pypi/smartypants)

## Usage

1. Put some text files into the `textfiles/` directory. (If you don't have any, try [Project Gutenberg](https://www.gutenberg.org/))
2. Start the MongoDB server
3. Run `textfiles-to-mongodb.py`

❗️ Note: The script will overwrite the entire collection in the database.

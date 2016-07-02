# textfiles-to-mongodb

A python script to parse a bunch of english-language text files and try to **extract sentences**. The results are stored in a MongoDB collection, one entry for every sentence. A document in the collection will look like this:

    {  
      u'_id':ObjectId('5777f6947eecd42dd933589e'),
      u'noOfWords':7,
      u'file':u'textfiles/pg1661.txt',
      u'sentence':u'"Then I do not see the point."'
    }

## Prerequesites

* [MongoDB](https://docs.mongodb.com/manual/installation/)
* [PyMongo](https://api.mongodb.com/python/current/tutorial.html)

## Usage

1. Put some text files into the `textfiles/` directory. (If you don't have any, try [Project Gutenberg](https://www.gutenberg.org/))
2. Start your MongoDB server
3. Run `textfiles-to-mongodb.py`

❗️ Note: The script will overwrite the data every time you run it.

## Todo

* Test more thoroughly
* Remove lost quotation marks (trailing at the beginning or end of a sentence)
* Consider replacing 'lazy' quotation marks with correct quotation marks
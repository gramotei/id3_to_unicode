#!/usr/bin/env python
#
#	id3_to_unicode.py -- change encoding of mp3 iD tags to unicode
#
# $Id: id3_to_unicode.py 259 2011-08-20 08:54:25Z lenik $

import os
import sys
import time

print "= id3_to_unicode.py = change encoding of mp3 iD3 tags to unicode, '-h' for help"
try :
	import codecs, types, chardet
	import eyeD3	# mp3 iD tag processing
except ImportError, e :
	print 'please, install python-%s' % str(e).split()[-1].lower()
	sys.exit()

import warnings	# UnicodeWarning: Unicode unequal comparison failed, blah-blah...
warnings.filterwarnings( 'ignore', category = UnicodeWarning )

help = """
	id3_to_unicode.py -- searches directories for .mp3 files,
	extracts iD3 tags and converts 'em to Unicode where possible.

	-r	search recursively (by default -- current directory only)
	-u	update mp3 files (by default -- perform 'dry run')
	-o	overwrite tags from Artist/Album/Title directory structure
	-h	print help (this page)

	The encoding statistics are calculated in every directory and easy
	cases are processed automatically. However, if statistics show
	there are several potential candidates for the proper encoding,
	the selection options/probabilities are given to the user.

	Wrong encoding choice usually results in encoding errors, therefore,
	please, use 'dry run' mode until you figure out the proper encoding,
	and only then use '-u' option to actually modify your files.

	Separate directories may have different iD3 tags encodings, but
	all files within the same directory are supposed to share the same
	encoding. Usually, every album is kept in the separate directory and
	this does not constitute any problems. However, if you have 2000+ mp3
	files with Chinese, Hebrew and Cyrillic tags in one large directory,
	they'd better be sorted beforehand.

	Missing iD3 tags are recreated from the file and/or directory names.
	For that purpose your music collection is supposed to be sorted by
	Artist/Album in separate directories:

		/home/user/Music/Artist/Album 2003/01 Song Title.mp3

	However, if all .mp3 files are already tagged, the directory
	structure is irrelevant and can be anything you like.

	Please, backup your .mp3 files before processing!

	Copyright(c) 2010-2012, lenik terenin
"""

path = '.'

recursive = False	# don't descend into subdirs
update_files = False	# don't touch files (require '-u' option)
overwrite_tags = False	# overwrite tags from Artist/Album/01 Title.mp3 structure

#sys.stdin = codecs.getreader("UTF8")(sys.stdin)
sys.stdout = codecs.getwriter("UTF8")(sys.stdout)

for i in sys.argv[1:] :
	if i.startswith( '-' ) :
		for c in i[1:].lower() :
			if c == 'r' :	# recursive
				recursive = True
			if c == 'u' :	# update files
				update_files = True
			if c == 'o' :	# overwrite tags
				overwrite_tags = True
			if c == 'h' :	# help
				print help
				sys.exit()
	else :
		path = i

def unicode2bytestring( string ) :
	try :
		string = ''.join( [chr(ord(i)) for i in string] )
	except ValueError :
		pass	# unicode fails chr(ord()) conversion
	return string

def make_unicode( string, encoding ) :
	try :
		string = unicode( string, encoding )
	except :
		pass	# bad encoding, do nothing
	return string

def convert( file_name, encoding ) :
	print unicode( file_name, "utf-8" ),
	if not eyeD3.isMp3File( file_name ) :
		print ': not an MP3 file'
		return

	try:
		tag = eyeD3.Tag()
		if not tag.link( file_name ) :
			tag.header.setVersion( eyeD3.ID3_V2_3 )
	except:
		tag.header.setVersion( eyeD3.ID3_V2_3 )
		pass

	artist = unicode2bytestring( tag.getArtist() )
	album = unicode2bytestring( tag.getAlbum() )
	title = unicode2bytestring( tag.getTitle() )

	original = ''.join( (artist,album,title) )

#	artist = artist.replace( '-', '' )
#	album = album.replace( '[+digital booklet]', '2010' )

	artist = make_unicode( artist, encoding )
	album = make_unicode( album, encoding )
	title = make_unicode( title, encoding )

	head, tail = os.path.split( os.path.abspath( file_name ) )
	if overwrite_tags or not len(title) :
		title = unicode( tail, 'utf-8' )[:-4]	# strip trailing ".mp3"
		if title[0] in '0123456789' and title[1] in '0123456789' and title[2] == ' ' :
			title = title[3:]	# strip leading track number

	head, tail = os.path.split( head )
	if overwrite_tags or not len(album) :
		album = unicode( tail, 'utf-8' )

	head, tail = os.path.split( head )
	if overwrite_tags or not len(artist) :
		artist = unicode( tail, 'utf-8' )

	if original != ''.join( (artist,album,title) ) :
		if update_files :
			# eyeD3.tag.TagException: ID3 v1.x supports ISO-8859 encoding only
			tag.setVersion( eyeD3.ID3_V2_4 )
			tag.setTextEncoding( eyeD3.UTF_8_ENCODING )
			tag.setArtist( artist )
			tag.setAlbum( album )
			tag.setTitle( title )
			tag.update()
		print '->',
	else :
		print '==', 

	print artist, ':', album, ':', title

stats = dict()

def collect_stats( file_name ) :
	global stats
	if not eyeD3.isMp3File( file_name ) :
		print unicode( file_name, "utf-8" ), ': not an MP3 file'
		return

	try:
		tag = eyeD3.Tag()
		if not tag.link( file_name ) :
			print unicode( file_name, "utf-8" ), ': iD3 tag is missing'
			return
	except Exception, e :
		print unicode( file_name, "utf-8" ), ':', str(e)
		return

	for i in (tag.getArtist(), tag.getAlbum(), tag.getTitle()) :
		enc = chardet.detect( unicode2bytestring( i ) )

		if enc['encoding'] == 'ascii' and not overwrite_tags : continue

		if enc['encoding'] == None : enc['encoding'] = 'None'

		if enc['encoding'] in stats :
			stats[enc['encoding']] += enc['confidence']
		else :
			stats[enc['encoding']] = enc['confidence']

def select_encoding( stats ) :
	if len(stats) == 1 :	# only one encoding is available
		return stats[0][1]

	if stats[0][0] - stats[1][0] > 40 :	# more than 40% difference
		return stats[0][1]

	stats = [i for i in stats if i[1] != 'None']

	print unicode(root,'utf-8'), ": several encodings are possible:"
	for i in xrange(len(stats)) :
		print "%d. %s (%5.2f%%)" % (i+1, stats[i][1], stats[i][0])

	while True :
		print 'select encoding (1..%d):' % (len(stats)),
		encoding = int(raw_input()) - 1
		try :
			print stats[encoding][1], 'selected'
			break
		except:
			pass
	return stats[encoding][1]

try:
	for root,dirs,files in os.walk( path ) :
		if not len(files) : continue

		stats = dict()
		for name in files :
			if name.lower().endswith('mp3') :
				collect_stats( os.path.join( root, name ) )

		if len(stats) :
			stats = [(stats[i],i) for i in stats]
			stats = sorted( stats, reverse = True )
			total = sum( [i[0] for i in stats] ) + 0.0001
			stats = [(i[0]*100/total,i[1]) for i in stats]

			encoding = select_encoding(stats)
			for name in files :
				if name.lower().endswith('.mp3') :
					convert( os.path.join( root, name ), encoding )
		else :
			print unicode(root,'utf-8'), ': nothing to convert or already in unicode/ascii',
		print
		if not recursive :
			break

except KeyboardInterrupt :
	print 'Ctrl/C was pressed, aborting...'
	pass


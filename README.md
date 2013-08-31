id3_to_unicode
==============

convert encoding of mp3 iD3 tags to unicode automatically

This small utility searches directories for .mp3 files, extracts iD3 tags and converts them to Unicode where possible. I wrote it because my new mp3 player barfed on non-unicode characters in tags and I wanted to fix all of my music collection (which includes a lot of internationally tagged songs) at once, without manual encoding input for every song. You may check Options page for detailed explanation.

Disclaimer
==============

This is a fork of the https://code.google.com/p/id3-to-unicode/ project originally created by lenik.terenin.

Encodings
==============

Basically, multiple encodings are supported, including Chinese, Japanese, Russian/Cyrillic, Hebrew and many others. Encoding is selected mostly automagically, but in some rare difficult cases user input might still be required.

Separate directories may have different iD3 tags encodings, but all files within the same directory are supposed to share the same encoding. Usually, every album is kept in the separate directory and this does not constitute any problems. However, if you have 2000+ mp3 files with Chinese, Hebrew and Cyrillic tags in one large directory, they'd better be sorted beforehand.

Missing iD3 tags
==============

Missing iD3 tags are recreated from the file and/or directory names. For that purpose your music collection is supposed to be sorted by Artist/Album in separate directories:

        /home/user/Music/Artist/Album 2003/01 Song Title.mp3

Requirements
==============

Plain Python installation is usually sufficient, however you might need to install python-chardet and python-eyed3 packages if these were not 
installed before. I haven't tested this on Windows, so feedback from win-users is very welcome.

A word of wisdom =)
==============

Please, backup your .mp3 files before processing!
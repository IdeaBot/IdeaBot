# ./reactions #

This folder is for reaction-based commands ("Reactions"). 
To create a reaction, write a python file (ending in `.py`) which declares a class named `Reaction`.
Place the python file in this folder (or a subfolder), and Idea will load the reaction next time you restart it.

To learn how to make your own reaction, check out 
[the Reaction interface documentation](https://github.com/NGnius/IdeaBot/wiki/Making-Reaction-based-Commands)

### Loading Mechanism ###

Files in `./reactions` are loaded alphabetically, following regular Python sorting (`sort()` and `sorted()`). 
Subfolders do not take priority, instead the folder itself is handled like a file.
Files in a subfolder are loaded alphabetically when it's the folder's turn.

Eg. Consider the following directory:
```
./reactions/
    reaction1.py
    datafile1.txt
    !subfolder/
        reaction2.py
        datafile2.csv
```

`!subfolder`, when sorted, will be the first file/folder in `./reactions/`. 
That means anything in `!subfolder` will be loaded first, so `reaction2.py` will be the first reaction loaded.
Then `reaction1.py` will be loaded next, since there are no other files ending in `.py` in `!subfolder`.
The other files, `datafile1.txt` and `datafile2.csv`, will be ignored since they do not end in `.py`.

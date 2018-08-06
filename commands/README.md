# ./commands #

This folder is for commands. 
To create a command, write a python file (ending in `.py`) which declares a class named `Command`.
Place the python file in this folder (or a subfolder), and Idea will load the command next time you restart it.

To learn how to make your own command, check out 
[the Command interface documentation](https://github.com/NGnius/IdeaBot/wiki/Making-Commands)

### Loading Mechanism ###

Files in `./commands` are loaded alphabetically, following regular Python sorting (`sort()` and `sorted()`). 
Subfolders do not take priority, instead the folder itself is handled like a file.
Files in a subfolder are loaded alphabetically when it's the folder's turn.

Eg. Consider the following directory:
```
./commands/
    command1.py
    datafile1.txt
    !subfolder/
        command2.py
        datafile2.csv
```

`!subfolder`, when sorted, will be the first file/folder in `./commands/`. 
That means anything in `!subfolder` will be loaded first, so `command2.py` will be the first command loaded.
Then `command1.py` will be loaded next, since there are no other files ending in `.py` in `!subfolder`.
The other files, `datafile1.txt` and `datafile2.csv`, will be ignored since they do not end in `.py`.

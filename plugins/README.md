# ./plugins #

This folder is for plugins. 
To create a plugin, write a python file (ending in `.py`) which declares a class named `Plugin`.
Place the python file in this folder (or a subfolder), and Idea will load the plugin next time you restart it.

To learn how to make your own plugin, check out 
[the Plugin interface documentation](https://github.com/NGnius/IdeaBot/wiki/Making-Plugins)

### Loading Mechanism ###

Files in `./plugins` are loaded alphabetically, following regular Python sorting (`sort()` and `sorted()`). 
Subfolders do not take priority, instead the folder itself is handled like a file.
Files in a subfolder are loaded alphabetically when it's the folder's turn.

Eg. Consider the following directory:
```
./plugins/
    plugin1.py
    datafile1.txt
    !subfolder/
        plugin2.py
        datafile2.csv
```

`!subfolder`, when sorted, will be the first file/folder in `./plugins/`. 
That means anything in `!subfolder` will be loaded first, so `plugin2.py` will be the first plugin loaded.
Then `plugin1.py` will be loaded next, since there are no other files ending in `.py` in `!subfolder`.
The other files, `datafile1.txt` and `datafile2.csv`, will be ignored since they do not end in `.py`.


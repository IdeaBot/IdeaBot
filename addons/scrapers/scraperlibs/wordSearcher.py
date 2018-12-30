"""This is for finding words in a given string, ignoring spaces
(if you want it to look for spots with spaces then add a space before
and one after the word you are looking before giving it to the function"""
def wordSearcher(wordToFind, stringToSearch, output="firstChar", multipleLocs=True):
    '''(str, str [, str, bool]) -> list of int
    search for wordToFind in stringToSearch
    soon to be deprecated'''
    wordLocations = []
    if wordToFind in stringToSearch: #no point going through the whole string if there isn't a possible match to start with
        for charNum in range(len(stringToSearch)): #search through the string sequentially from char 0 to end
            if stringToSearch[charNum:(charNum+len(wordToFind))]== wordToFind: #play the matching game, if you win append the result to the wordLocations list
                if output.lower()=="firstchar": #make sure that only if the program wants the first char you give them the first char
                    wordLocations.append(charNum)

                elif output.lower()=="lastchar": #if they want the last char, make it so!
                    wordLocations.append(charNum+len(wordToFind))

                elif output.lower()=="uptoword": #if they want the searched string up to the word, give them that
                    wordLocations.append(stringToSearch[:charNum])

                elif output.lower()=="uptoandword": #if they want the searched string up to the end of the word, engage!
                    wordLocations.append(stringToSearch[:charNum+len(wordToFind)])

                if not multipleLocs: #in case they just want the first case end the function here
                        return wordLocations
    return wordLocations

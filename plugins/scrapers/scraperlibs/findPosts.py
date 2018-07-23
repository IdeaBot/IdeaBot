import wordSearcher
def FirstPost(rawpage):
    '''(str) -> url: str
    finds the first post in a forum section, through the use of (coding) magic'''
    lastUpdateLoc = wordSearcher.wordSearcher(" and was last updated by", rawpage, multipleLocs = False)[0]
    FirstPostLinkStart = lastUpdateLoc + wordSearcher.wordSearcher(" href=\"", rawpage[lastUpdateLoc:], output="lastChar")[2] #see note below about why that's a two
    '''Since the format is "last updated by [username link] [time elapsed and link to post] ago",
    and for some reason the user's profile is linked twice (don't ask me, I didn't write the website - I'm just cringing from it),
    the 3rd (2nd if you start from 0) href=" after "last updated by" is the link to the post'''
    FirstPostLinkEnd = FirstPostLinkStart + wordSearcher.wordSearcher("\"", rawpage[FirstPostLinkStart:], multipleLocs = False)[0] #find the closing " for the url
    return rawpage[FirstPostLinkStart:FirstPostLinkEnd]

def FindPosts(rawpage):
    '''(str) -> list of url : str
    finds all posts in a forum section'''
    agoLocs = wordSearcher.wordSearcher(" ago", rawpage)[1:] #[1:] is to ignore the top part of each forum section which displays the most recently updated topic
    posts = []
    for loc in agoLocs:
        try:
            linkStart = (loc-wordSearcher.wordSearcher("\"=ferh", rawpage[loc::-1], multipleLocs=False)[0])+len("\"")
            linkEnd = linkStart+wordSearcher.wordSearcher("\"", rawpage[linkStart:], multipleLocs=False)[0]
            posts.append(rawpage[linkStart:linkEnd])
        except:
            print("Invalid ago location found")
    return posts

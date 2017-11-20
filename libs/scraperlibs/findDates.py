import wordSearcher, time
def findDates(textpage):
    '''(str) -> list of struct_time objects
    strip time from forum thread with time.strptime'''
    dateEnds = wordSearcher.wordSearcher(" at ", textpage) #the first thing that always come after a date is "at [time]", so this finds what is right after the date
    dates = []
    for i in dateEnds: #strip the date from every suspected date
        try: #don't crash in case the suspected date is just someone who wrote " at " in their post
            dates.append([time.strptime(textpage[i-len("dd/mm/yyyy"):i], "%d/%m/%Y"),i])
        except:
            pass #don't do anything if someone wrote " at " in their post
    return dates

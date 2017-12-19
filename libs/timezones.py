import dataloader

timezones = dataloader.datafile("./data/timezones.csv")

def findUTCDifference(string):
    '''(str) -> (int,int)
    converts a timezone in acronym, full or UTC+/-## form to (hours,minutes) difference from UTC
    Precondition: strip your fucking strings if you're not sure if they have whitespaces'''
    try:
        return int(string[-3:])
    except ValueError:
        pass

    for i in timezones.content:
        if i[0] == string or i[1] == string:
            if ":" in i[2]:
                time = i.split(":")
                time[0] = int(time[0][-3:])
                time[1] = int(time[1]) * time[0]//abs(time[0]) # time[0]/abs(time[0]) transfers the sign of time[0] without the magnitude
                return time[0],time[1] # hour, minutes
            else:
                print(i[2][-3:])
                return int(i[2][-3:]), 0

def getTimezone(string):
    '''(str) -> str
    returns the timezone in string'''
    for i in timezones.content:
        for j in i:
            if j in string:
                return j
    return -1

def findTimezone(string):
    '''(str) -> int
    returns the index of the first timezone in string'''
    for i in timezones.content:
        for j in i:
            try:
                return string.index(j)
            except ValueError:
                pass
    return -1

def findTime(string):
    '''(str) -> int
    returns the index of the first time in string
    Precondition: string must contain a time in form HH:MM (to get an output)'''
    maybeTimes = string.split(":")
    for i in range(1, len(maybeTimes)):
        try:
            int(maybeTimes[i-1][-2:])
            int(maybeTimes[i][:2])
            return string.find(maybeTimes[i-1][-2:] + ":" + maybeTimes[i][:2])
        except ValueError:
            pass

def stripTime(string):
    '''(str) -> list of str
    converts string to [time, timezone]
    Precondition: string must contain a time and timezone, together'''
    timezoneLoc = findTimezone(string)
    splitstring = string[:timezoneLoc].split()
    timezone = getTimezone(string)
    return [time, timezone]

def getConversionParameters(msg):
    '''(str) -> (str, str)
    converts a msg into the parameters that convert() needs
    Precondition: msg must contain two timezones and a time in a format similar to "##:## timezone in/to timezone" '''
    splitmsg = msg.split(" in")
    for i in range(len(splitmsg)-1):
        if ":" in splitmsg[i]:
            fromtime = stripTime(splitmsg[i])
            targetTimezone = getTimezone(splitmsg[i+1])
            if targetTimezone != -1 and fromtime[0][-2:].isnumeric():
                print(fromtime[0]+" "+fromtime[1], targetTimezone)
                return fromtime[0]+" "+fromtime[1], targetTimezone
    print("Nothing found!!!!!!! Using backup option")
    return findTime(msg)+ " " + getTimezone(msg), "UTC+00"



def convert(fromtime, targetTimezone):
    '''(str, str) -> int
    converts fromtime, in some form resembling a time, to the same time in targetTimezone'''
    time = stripTime(fromtime)
    time[0] = time[0].split(":")
    timezone2 = getTimezone(targetTimezone)
    print(timezone2)
    print(time[1])
    timeDiff1 = findUTCDifference(time[1])
    timeDiff2 = findUTCDifference(timezone2)
    timeDiffHours = timeDiff2[0] - timeDiff1[0] #utc-5 -> utc-2 = +3
    timeDiffMinutes = timeDiff2[1] - timeDiff1[1]
    time[0][0] = str(timeDiffHours + int(time[0][0]))
    time[0][1] = str(timeDiffMinutes + int(time[0][1]))
    for i in range(len(time[0])):
        if len(time[0][i]) < 2:
            time[0][i] = "0"+time[0][i]
    return time[0][0]+":"+time[0][1] + " " + timezone2 # nicely formated thing (unlike the rest of this file)

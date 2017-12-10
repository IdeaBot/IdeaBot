import dataloader

timezones = dataloader.datafile("./timezones.csv")

def findUTCDifference(string):
    '''(str) -> int
    converts a timezone in acronym, full or UTC+/-## form to int
    Precondition: strip your fucking strings if you're not sure if they have whitespaces'''
    try:
        return int(string[-3:])
except ValueError:
        pass

    for i in timezone.content:
        if i[0] == string or i[1] == string:
            if ":" in i[2]:
                time = i.split(":")
                time[0] = int(time[0][-3:])
                time[1] = int(time[1]) * time[0]//abs(time[0]) # time[0]/abs(time[0]) transfers the sign of time[0] without the magnitude
                return time[0],time[1] # hour, minutes
            else:
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
            return string.find(maybeTimes[i-1][-2:] + ":" maybeTimes[i][:2])
        except ValueError:
            pass

def stripTime(string):
    '''(str) -> list of str
    converts string to [time, timezone]
    Precondition: string must contain a time and timezone, together'''
    timezoneLoc = findTimezone(string)
    time = string[:timezoneLoc].split()[-1]
    timezone = getTimezone(string)
    return [time, timezone]


def convert(fromtime, targetTimezone):
    '''(int, str) -> int
    converts fromtime, in some form resembling a time, to the same time in timezone to'''
    time = stripTime(fromtime)
    time[0] = time[0].split(":")
    timezone2 = findTimezone(targetTimezone)
    timeDiff = findUTCDifference(timezone2)- findUTCDifference(time[1]) #utc-5 -> utc-2 = +3
    time[0][0] += timeDiff
    time[0][1] += int((time[0][0]%1)*60)
    time[0][0] = int(time[0][0]//1)
    return str(time[0][0])+":"+str(time[0][1]) + timezone2

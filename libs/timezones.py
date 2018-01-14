# this badly needs to be changed to OOP, because it's rly hurtful to understand right now
from libs import dataloader

timezones = dataloader.datafile("./data/timezones.csv")

class SimpleTime:
    ''' stores a time in an easy format '''
    def __init__(self, time):
        ''' (SimpleTime, str) -> None
        str must be a time in format (H)H:MM where HH and MM are valid positive integers
        Do I rly need to say what __init__ does? '''
        timeSplit = time.split(":")
        try:
            if "am" == timeSplit[0][-2:].lower():
                self.hour = int(timeSplit[0][:-2])
            elif "pm" == timeSplit[0][-2:].lower():
                self.hour = int(timeSplit[0][:-2])
                self.hour += 12
            else:
                self.hour = int(timeSplit[0])
        except:
            raise ValueError("Invalid time")
        try:
            if "am" == timeSplit[1][-2:].lower():
                self.minute = int(timeSplit[1][:-2])
            elif "pm" == timeSplit[1][-2:].lower():
                self.hour += 12
                self.minute = int(timeSplit[1][:-2])
            else:
                self.minute = int(timeSplit[1])
        except:
            self.minute = 0
        self.time = time
        self.unfuckify()
        #print(time, self.hour, self.minute) # best debug

    def __str__(self):
        ''' (SimpleTime) -> str
        returns a HH:MM string '''
        hour = str(self.hour)
        if len(hour)==1:
            hour = "0"+hour
        minute = str(self.minute)
        if len(minute)==1:
            minute = "0"+minute
        return hour+":"+minute

    def unfuckify(self):
        ''' (SimpleTime object) -> int
        make sure hour < 24 and minute < 60 and return amount that hour is fucked up by '''
        self.hour += self.minute // 60
        self.minute = self.minute % 60
        extra = self.hour // 24
        self.hour = self.hour % 24
        return extra

    def add(self,hour, minute=0):
        ''' (SimpleTime object, int, int) -> int
        Add hour to SimpleTime.hour and add minute to SimpleTime.minute '''
        self.hour += hour
        self.minute += minute
        return self.unfuckify()

    def addTime(self, time):
        ''' (SimpleTime object, SimpleTime object) -> int
        Add time.hour to self.hour and and add time.minute to self.minute and return offset in days'''
        self.hour += time.hour
        self.minute += time.minute
        return self.unfuckify()

    def subtract(self, hour, minute=0):
        ''' (SimpleTime object, int, int) -> int
        Subtract hour from SimpleTime.hour and subtract minute from SimpleTime.minute '''
        self.hour -= hour
        self.minute -= minute
        return self.unfuckify()

    def subtractTime(self, time):
        ''' (SimpleTime object, SimpleTime object) -> int
        Add time.hour to self.hour and and add time.minute to self.minute and return offset in days'''
        self.hour -= time.hour
        self.minute -= time.minute
        return self.unfuckify()

class Timezone:
    ''' stores a timezone in an easy format '''

    def __init__(self, timezone):
        self.timezonesIndex = -1
        for i in range(len(timezones.content)):
            if timezone in timezones.content[i]:
                self.timezonesIndex = i
                self.acronym = timezones.content[i][0]
                self.name = timezones.content[i][1]
                self.utc = timezones.content[i][2]
                self.conversion = SimpleTime(self.utc[4:])
                self.conversionSign = self.utc[3]
                break
        if self.timezonesIndex == -1: raise ValueError("Invalid timezone")


class FullTime:
    ''' stores a time and it's timezone in an easy format '''
    def __init__(self, time, timezone, extraDays = 0):
        '''(FullTime object, SimpleTime object, Timezone object) -> None
        initializes variables'''
        self.time = time
        self.timezone = timezone
        self.extraDays = extraDays

    def __str__(self):
        ''' (FullTime object) -> str
        returns a string of the FullTime object, in form HH:MM TimezoneAcronym'''
        if self.extraDays > 0:
            return str(self.time) + " " + self.timezone.acronym + " +" + str(self.extraDays) + " day"
        elif self.extraDays < 0:
            return str(self.time) + " " + self.timezone.acronym + " " + str(self.extraDays) + " day"
        else:
            return str(self.time) + " " + self.timezone.acronym

    def convertTo(self, timezone):
        ''' (FullTime object, str or Timezone object) -> FullTime object
        returns the FullTime object equivalent in timezone '''
        if "Timezone" not in str(type(timezone)):
            try:
                timezone = Timezone(timezone)
            except ValueError:
                raise ValueError("timezone is not a Timezone object nor a valid string timezone")
        newTime = SimpleTime(str(self.time)) # make a copy of self.time
        extraDays = 0
        if self.timezone.conversionSign == "+":
            extraDays += newTime.subtractTime(self.timezone.conversion)
        else:
            extraDays += newTime.addTime(self.timezone.conversion)
        if timezone.conversionSign == "+":
            extraDays += newTime.addTime(timezone.conversion)
        else:
            extraDays += newTime.subtractTime(timezone.conversion)
        return FullTime(newTime, timezone, extraDays)

def getConversionParameters(msg):
    '''(str) -> (FullTime object, Timezone object)
    converts a msg into the parameters that convert() needs
    Precondition: msg must contain two timezones and a time in a format similar to "##:## timezone in/to timezone" '''
    splitmsg = msg.split(" ")
    for i in range(len(splitmsg)-3):
        try:
            time = SimpleTime(splitmsg[i])
            if splitmsg[i+1][-1].lower() =="m" and i < len(splitmsg)-4:
                if splitmsg[i+1].lower() == "pm": time.add(12)
                i += 1
            try:
                timezone = Timezone(splitmsg[i+1])
                try:
                    timezone2 = Timezone(splitmsg[i+3])
                    return FullTime(time, timezone), timezone2
                except ValueError:
                    pass
            except ValueError:
                pass
        except ValueError:
            pass

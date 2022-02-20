from csv import DictReader
import datetime as dt

fileundertest = 'test.csv'
time_format = '%H:%M:%S'
workingfile = open(fileundertest)
reader = DictReader(workingfile)
isFirstRun = True
isCooling = False
isHeating = False

def report_transition(starttime, row):
    start = dt.datetime.strptime(starttime, time_format)
    end = dt.datetime.strptime(row['Time'], time_format)
    et = end - start
    start_format = round(et.seconds / 60, 1)
    print("From {} to {} in {} minutes...".format(starttemp, target, start_format))

def report_intermediate(starttime, row, intermediate):
    start = dt.datetime.strptime(starttime, time_format)
    end = dt.datetime.strptime(row['Time'], time_format)
    et = end - start
    start_format = round(et.seconds / 60, 1)
    print("From {} to {} in {} minutes...".format(starttemp, intermediate, start_format))

for row in reader:
    #initialize previousSP with first SP found
    if(isFirstRun):
        previousSP = float(row['TEMPERATURE SP'])
        isFirstRun = False
    else:
        #start tracking a transition when current SP has changed from previousSP
        if(float(row['TEMPERATURE SP']) != previousSP):
            starttemp = previousSP
            target = float(row['TEMPERATURE SP'])
            starttime = row['Time']
            isCooling = ( previousSP > target)
            isHeating = (previousSP < target)
            previousSP = float(row['TEMPERATURE SP'])
        else:
            if(isCooling):
                if(float(row['TEMPERATURE PV']) <= float(target)):
                    isCooling = False
                    report_transition(starttime, row)
            elif(isHeating): 
                if(float(row['TEMPERATURE PV']) >= float(target)):
                    isHeating = False
                    report_transition(starttime, row)
print('Finished!')



import csv

nf = open("data/ga_logs/AUDUSD240xl.csv","w")
writer = csv.writer(nf,delimiter=",",quotechar='"')

with open("data/ga_logs/AUDUSD240.csv","r") as of:
    reader = csv.reader(of,delimiter=",",quotechar='"')
    for row in reader:
        writer.writerow(row[:5])




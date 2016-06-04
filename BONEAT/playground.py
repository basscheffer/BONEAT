import csv
import cStringIO
import codecs

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

import ast
#
# text = """THIS IS
# A VERY
# WEIRD
# FORMAT
# OF TEXT
# 312
# 792481
# 21611
# #;xxx"""
# d={"profit":3000,"drawdown":20}
# example_list =[1.03,300,"performance",text,d]
#
# for i in range(5):
#     with open('eggs.csv', 'a') as csvfile:
#         spamwriter = csv.writer(csvfile, delimiter=',',quotechar='"')
#         spamwriter.writerow(example_list)

#
newlist = []
with open('data/ga_logs/AUDUSD240.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',',quotechar='"')
    for row in reader:
        newlist.append(row)
newlist[0][0]='1'
with open('data/ga_logs/AUDUSD240fit.csv', 'w') as newf:
    writer = UnicodeWriter(newf, delimiter=',',quotechar='"')
    for row in newlist:
        writer.writerow(row[:5])
with open('data/ga_logs/AUDUSD240fit.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',',quotechar='"')
    for row in reader:
        print row



# with open('data/ga_logs/AUDUSD240utf.csv', 'r') as csvfile:
#     nf = open('data/ga_logs/AUDUSD240pt1.csv', 'w')
#     writer = UnicodeWriter(nf, delimiter=',',quotechar='"')
#     reader = csv.reader(csvfile, delimiter=',',quotechar='"')
#     for row in reader:
#         # print ast.literal_eval(row[4])
#         writer.writerow(row)
#     nf.close()

# nf = open("data/ga_logs/AUDUSD240pt1.csv","wb")
# of = open("data/ga_logs/AUDUSD240utfBU.csv","r")
# for line in of:
#     print line
# of.close()
# nf.close()




import os
import datetime

base_dir = "data/raw_price_data/"
datadict = {}

for file in os.listdir(base_dir):

    if file.endswith(".csv"):
        name = file.split('.')[0]
        pair = name[:6]
        tf = name[6:]
        tl = [0]*2

        with open(base_dir+file) as fh:
            ds = fh.readline().split(",")[0]
            tl[0] = datetime.datetime.strptime(ds,"%Y.%m.%d")
            for line in fh:
                pass
            ds = line.split(",")[0]
            tl[1] = datetime.datetime.strptime(ds,"%Y.%m.%d")

        if pair in datadict:
            datadict[pair].update({tf:tl})
        else:
            datadict[pair] = {tf:tl}

print datadict
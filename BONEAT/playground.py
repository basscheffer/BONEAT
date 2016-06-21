import genome
import sumulateN as simulate
import MySQLdb as db

conn = db.connect(host="basdb.cjezotpxmuuq.ap-southeast-2.rds.amazonaws.com"
                             ,port=3306
                             ,user = "basscheffer"
                             ,passwd ="basscheffer"
                             ,db="boneat")
curs = conn.cursor()
query = """select genotype_id, fitness, gt_string from genotypes where genotype_id = 150"""

S = {"spread":1.8,"profit_norm":0.627450,"traindata_start":"2007-01-01","traindata_end":"2013-01-01"}
dp = "data/npy_data/AUDUSD240_NormData.npy"

curs.execute(query)
result = curs.fetchall()

for row in result:
    print "Genome %i with fitness %f"%(row[0],row[1])
    G = genome.buildFromGTFile(row[2])
    data = [G,dp,S]
    print simulate.simuRoutine(data)




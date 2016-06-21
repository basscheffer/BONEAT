import MySQLdb
import random

class GTLogger:

    def __init__(self,host="basdb.cjezotpxmuuq.ap-southeast-2.rds.amazonaws.com"
                             ,port=3306
                             ,user = "basscheffer"
                             ,passwd ="basscheffer"
                             ,database="boneat"):
        self.host = host
        self.port = 3306
        self.user = user
        self.password = passwd
        self.db = database

        self.connect()

    def connect(self):
        self.conn = MySQLdb.connect(host=self.host,port=self.port,user = self.user,passwd =self.password,db=self.db)
        self.curs = self.conn.cursor()

    def logGenoType(self,data,genotype_string,cull):
        query = """select min(t.fitness)
        from (select fitness from genotypes order by fitness desc limit %i)t"""%(cull)
        self.curs.execute(query)
        floor = self.curs.fetchall()[0][0]
        if data["fitness"] < floor:
            return

        I_Q = """insert
        into genotypes
        (pair,generation,species,slope*r2,slope,profit,trades,winratio,drawdown,r2,fitness,confirmfactor,gt_string)
        values ('%(pair)s',%(generation)s,%(species)s,%(slope*r2)s,%(slope)s,%(profit)s,%(trades)s,%(winratio)s,%(drawdown)s
        ,%(r2)s,%(fitness)s,%(confirmfactor)s,'%(gt_string)s')"""
        data.update({"gt_string":genotype_string})
        query = I_Q%data
        self.curs.execute(query)
        self.conn.commit()

    def cullGenoTypeLog(self,cull):
        query = """DELETE FROM genotypes
        WHERE genotype_id NOT IN
        (select * from(select genotype_id from genotypes order by fitness desc limit %i)t)"""%(cull)
        self.curs.execute(query)
        self.conn.commit()

    def close(self):
        self.conn.close()

# conn = MySQLdb.connect(host="basdb.cjezotpxmuuq.ap-southeast-2.rds.amazonaws.com"
#                              ,port=3306
#                              ,user = "basscheffer"
#                              ,passwd ="basscheffer"
#                              ,db="boneat")
# curs = conn.cursor()
# curs.execute("select fitness from genotypes order by fitness desc limit 100")
# res = curs.fetchall()
# print res
# print int(res[99][0])
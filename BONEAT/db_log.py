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

    def logGenoType(self,data,genotype_string,cull,pool_id):
        query = """select min(t.fitness), count(t.fitness)
        from (select fitness from genotypes where pool_id = %i order by fitness desc limit %i)t"""%(pool_id,cull)
        self.curs.execute(query)
        res = self.curs.fetchall()
        if not res == None:
            if res[0][1] < cull:
                pass
            else:
                if data["fitness"] < res[0][0]:
                    return

        I_Q = """insert
        into genotypes
        (pair,generation,species,slope_r2,slope,profit,trades,winratio,drawdown,r2,fitness,confirmfactor,gt_string,pool_id)
        values ('%(pair)s',%(generation)s,%(species)s,%(slope*r2)s,%(slope)s,%(profit)s,%(trades)s,%(winratio)s,%(drawdown)s
        ,%(r2)s,%(fitness)s,%(confirmfactor)s,'%(gt_string)s',%(pool_id)s)"""
        data.update({"gt_string":genotype_string})
        query = I_Q%data
        self.curs.execute(query)
        self.conn.commit()

    def cullGenoTypeLog(self,cull,pool_id):
        query = """DELETE FROM genotypes
        WHERE genotype_id NOT IN
        (select * from(select genotype_id from genotypes where pool_id = %i order by fitness desc limit %i)t)
        AND pool_id = %i"""%(pool_id,cull,pool_id)
        self.curs.execute(query)
        self.conn.commit()

    def close(self):
        self.conn.close()

    def newPool(self,cfg_string):
        query = """INSERT INTO pools
        (cfg_string) VALUES ('%s')"""%(cfg_string)
        self.curs.execute(query)
        self.conn.commit()
        return self.curs.lastrowid


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
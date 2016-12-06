from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext

conf = SparkConf().setAppName("DataFrameOperationsTest").setMaster("local[*]")
sc = SparkContext(conf=conf)
sqlContext = SQLContext(sc)

df1_schema = ['id', 'name', 'turnOver', 'commAmt', 'country']
df1_data = [(1, "Customer1", 120000.00, 100.00, "USA"),
            (2, "Customer2", 100500.00, 500.00, "UK"),
            (3, "Customer3", 160500.00, 200.00, "IND"),
            (4, "Customer4", 110500.00, 100.00, "IND")]
df1 = sqlContext.createDataFrame(df1_data, df1_schema)

df2_schema = ['id', 'name', 'turnOver', 'commAmt', 'country']
df2_data = [(1, "Customer1", 120000.00, 100.00, "USA"),
            (2, "Customer2", 100500.00, 500.00, "UK"),
            (3, "Customer3", 160500.00, 200.00, "IND"),
            (4, "Customer4", 110500.00, 100.00, "IND")]
df2 = sqlContext.createDataFrame(df2_data, df2_schema)


# ---------------------------------------------------------------------------------
#                                Project
# ---------------------------------------------------------------------------------
from python.transformers.Transformers import Project, GroupBy

proj1 = Project("select", "id", "name", "turnOver", "country", "commAmt")
proj2 = Project ("select", "name", "turnOver", "country", "commAmt")
gb1 = GroupBy(["country", "id"], "min(commAmt)", "max(turnOver)")
gb2 = GroupBy(["country"], "min(commAmt)", "max(turnOver)")
# ---------------------------------------------------------------------------------
#                                DAG
# ---------------------------------------------------------------------------------

from DAG import DAG

"""dag1 = DAG().start(proj1).fork(proj1,[gb1,gb2]).setBindings({proj1:df1})
dag1 = DAG().start((proj1, "myproj1")).append(proj1, gb1).setBindings({proj1:df1})
dag1 = DAG().start([ proj1, proj2]).append(proj1, gb1).append(proj2, gb2).setBindings({proj1:df1,proj2:df2})"""

dag1 = DAG().start([(proj1,"myproj1"), (proj2, "myproj2")]).append(proj1, gb1).append(proj2, gb2).setBindings({proj1:df1,proj2:df2})


# ---------------------------------------------------------------------------------
#                                  pipe
# ---------------------------------------------------------------------------------
from IBMSparkPipeline import IBMSparkPipeline

pipeline = IBMSparkPipeline().setStages(dag1)
print pipeline.getRootLabels()
pipeline.save("dag1")

loadedpipeline = IBMSparkPipeline.load("dag1")

updatepipeline = loadedpipeline.updateBindings({"myproj1":df1, "myproj2":df2})
print loadedpipeline.getRootLabels()
result = updatepipeline.fit()

for item in result:
    item.show()

"""from IBMSparkPipeline import IBMSparkPipeline

pipeline = IBMSparkPipeline().setStages(dag1)

result = pipeline.fit()

for item in result:
    item.show()"""

"""from IBMSparkPipeline import IBMSparkPipeline

pipeline = IBMSparkPipeline().setStages(dag1)
pipeline.save("dag1")

loadedpipeline = IBMSparkPipeline.load("dag1")
updatepipeline = loadedpipeline.updateBindings({"myproj1":df1})
result = updatepipeline.fit()

for item in result:
    item.show()"""

"""from IBMSparkPipeline import IBMSparkPipeline

pipeline = IBMSparkPipeline().setStages(dag1)
result = pipeline.fit()

for item in result:
    item.show()"""














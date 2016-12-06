from pyspark import SparkConf, SparkContext
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.feature import HashingTF, Tokenizer
from pyspark.sql import Row, SQLContext

# Prepare training documents from a list of (id, text, label) tuples.
conf = SparkConf().setAppName("Pipeline Model Test").setMaster("local[*]")
sc = SparkContext(conf=conf)
sqlContext = SQLContext(sc)

from IBMSparkPipeline import IBMSparkPipeline
from IBMSparkPipelineModel import IBMSparkPipelineModel

LabeledDocument = Row("id", "text", "label")
training = sqlContext.createDataFrame([
    (0L, "a b c d e spark", 1.0),
    (1L, "b d", 0.0),
    (2L, "spark f g h", 1.0),
    (3L, "hadoop mapreduce", 0.0)], ["id", "text", "label"])

# Configure an ML pipeline, which consists of tree stages: tokenizer, hashingTF, and lr.
tokenizer = Tokenizer(inputCol="text", outputCol="words")
hashingTF = HashingTF(inputCol=tokenizer.getOutputCol(), outputCol="features")
lr = LogisticRegression(maxIter=10, regParam=0.01, thresholds=[0.5, 0.5])

pipeline = IBMSparkPipeline().setStages([tokenizer, hashingTF, lr])
model = pipeline.fit(training)
# print pipeline.jIBMSparkPipeline.getStages()
# print model
# print type(model)

model.save("model1")
loadedpipelinemodel = IBMSparkPipelineModel.load("model1")
df = loadedpipelinemodel.transform(training)
df.show()
#
# test = sqlContext.createDataFrame([
#     (4L, "spark i j k"),
#     (5L, "l m n"),
#     (6L, "mapreduce spark"),
#     (7L, "apache hadoop")], ["id", "text"])
#
# # Make predictions on test documents and print columns of interest.
# prediction = loadedpipelinemodel.transform(test)
# selected = prediction.select("id", "text", "prediction")
# for row in selected.collect():
#     print(row)

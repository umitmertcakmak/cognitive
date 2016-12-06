from pyspark import SparkConf, SparkContext
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.feature import HashingTF, Tokenizer
from pyspark.sql import Row, SQLContext

# Prepare training documents from a list of (id, text, label) tuples.
conf = SparkConf().setAppName("Pipeline test").setMaster("local[*]")
sc = SparkContext(conf=conf)
sqlContext = SQLContext(sc)

from IBMSparkPipeline import IBMSparkPipeline
from DAG import DAG
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
dag1 = DAG().start(tokenizer).append(tokenizer, hashingTF).append(hashingTF, lr).setBindings({tokenizer: training})

pipeline = IBMSparkPipeline().setStages(dag1)

# model = pipeline.fit(training)
model = pipeline.fit()

print type(model)
print type(model[0])

model[0].pipelineModel.save("model1")
loadedpipelinemodel = IBMSparkPipelineModel.load("model1")

df = loadedpipelinemodel.transform(training)
# df = model[0].pipelineModel.transform(training)
df.show()

test = sqlContext.createDataFrame([
    (4L, "spark i j k"),
    (5L, "l m n"),
    (6L, "mapreduce spark"),
    (7L, "apache hadoop")], ["id", "text"])

# Make predictions on test documents and print columns of interest.
prediction = model[0].pipelineModel.transform(test)
selected = prediction.select("id", "text", "prediction")
for row in selected.collect():
    print(row)

from pyspark.sql import SparkSession
from pathlib import Path

from demo_one.utils import preprocess  # Replace with the actual module containing your preprocess function
from pyspark.sql import SparkSession
import pandas as pd
import yaml

# spark = SparkSession.builder.appName("CSV Loading Example").getOrCreate()
# dbutils = DBUtils(spark)

with open('demo_one/tasks/config.yml', 'r') as file:
    configure = yaml.safe_load(file)

def test_preprocess(spark: SparkSession, tmp_path: Path):
    
    input_data = pd.read_csv('tests/test_df.csv')

    

    # Call the preprocess function
    df_feature, df_input = preprocess(spark, configure, input_data)

    # Convert the Spark DataFrames to Pandas DataFrames for easier comparison
    df_input_pandas = df_input.toPandas()
    df_feature_pandas = df_feature.toPandas()

    # Check if the number of rows in the output matches the input
    assert len(df_input_pandas) == len(input_data)
    assert len(df_feature_pandas) == len(input_data)

if __name__ == '__main__':
    test_preprocess()
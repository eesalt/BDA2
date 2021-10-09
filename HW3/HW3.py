import sys

from calculate_batting_average import CalculateBattingAverage
from pyspark import StorageLevel
from pyspark.ml import Pipeline
from pyspark.sql import SparkSession
from pyspark.sql.functions import round


def main():
    spark = SparkSession.builder.master("local[*]").getOrCreate()

    user = input("Enter your mariadb user: ")
    password = input("Enter the associated password: ")

    batter_counts_df = (
        spark.read.format("jdbc")
        .option("url", "jdbc:mysql://localhost:3306/baseball")
        .option("driver", "org.mariadb.jdbc.Driver")
        .option("dbtable", "batter_counts")
        .option("user", user)
        .option("password", password)
        .load()
    )

    batter_counts_df.createOrReplaceTempView("batter_counts")
    batter_counts_df.persist(StorageLevel.DISK_ONLY)

    game_df = (
        spark.read.format("jdbc")
        .option("url", "jdbc:mysql://localhost:3306/baseball")
        .option("driver", "org.mariadb.jdbc.Driver")
        .option("dbtable", "game")
        .option("user", user)
        .option("password", password)
        .load()
    )

    game_df.createOrReplaceTempView("game")
    game_df.persist(StorageLevel.DISK_ONLY)

    query = """
    SELECT a.game_id,
           a.batter,
           sum(c.atBat) at_Bats,
           sum(c.Hit) hits
    from batter_counts a,
         batter_counts c,
         (SELECT a.game_id, b.game_id as prior_game
        from game a,
        game b
        where a.local_date > b.local_date
    and b.local_date >= date_sub(date_trunc('DD',a.local_date),100)) d
    WHERE a.batter = c.batter
      and c.game_id = d.prior_game
      and a.game_id = d.game_id
    group by a.batter,
             a.game_id"""

    results_df = spark.sql(query)

    CalcBattAvg = CalculateBattingAverage(
        inputCols=["at_Bats", "hits"], outputCol="batting_average"
    )
    pipeline = Pipeline(stages=[CalcBattAvg])
    model = pipeline.fit(results_df)
    batting_average_df = model.transform(results_df)
    rounded_ba_df = batting_average_df.withColumn(
        "Rounded_Batting_Avg", round(batting_average_df["batting_average"], 3)
    )
    rounded_ba_df.show()

    return


if __name__ == "__main__":
    sys.exit(main())

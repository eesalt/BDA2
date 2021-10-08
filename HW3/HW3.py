import sys

from pyspark import StorageLevel
from pyspark.sql import SparkSession


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
           CASE WHEN sum(c.atBat) > 0 THEN
           round(sum(c.Hit) / sum(c.atBat), 3)
               ELSE NULL END as 100_Day_Batting_Average
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
    results_df.show()

    return


if __name__ == "__main__":
    sys.exit(main())

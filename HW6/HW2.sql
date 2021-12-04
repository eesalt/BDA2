DROP INDEX IF EXISTS game_id ON batter_counts;

CREATE INDEX game_id ON batter_counts(game_id);

DROP TABLE IF EXISTS batter_ba;

CREATE TABLE batter_ba as
SELECT a.batter,
       CASE WHEN sum(a.atBat)>0 THEN
       round(sum(a.Hit) / sum(a.atBat),3)
        ELSE NULL END as Batting_Average
from batter_counts a
group by a.batter;

DROP TABLE IF EXISTS batter_annual_ba;

CREATE TABLE batter_annual_ba as
SELECT a.batter,
       year(b.local_date)        as YEAR,
       CASE WHEN sum(a.atBat) > 0 THEN
       round(sum(a.Hit) / sum(a.atBat),3)
           ELSE NULL END as Batting_Average
from batter_counts a,
     game b
WHERE a.game_id = b.game_id
group by a.batter,
         year
order by 1, 2;

DROP TABLE IF EXISTS batter_100_day_ba;

CREATE TABLE batter_100_day_ba as
SELECT a.game_id,
       a.batter,
       CASE WHEN sum(c.atBat) > 0 THEN
       round(sum(c.Hit) / sum(c.atBat), 3)
           ELSE NULL END as 100_Day_Batting_Average
from batter_counts a,
     game b,
     batter_counts c
WHERE a.batter = c.batter
  and a.game_id = b.game_id
  and c.game_id < a.game_id
  and c.game_id in
    (select min(game_id) from game g where g.local_date >= date_add(b.local_date, INTERVAL -100 DAY))
group by a.batter,
         a.game_id;

COMMIT;
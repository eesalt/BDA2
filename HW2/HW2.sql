USE baseball;

# You have probably already corrected this
#ALTER TABLE inning MODIFY COLUMN game_id INT UNSIGNED NOT NULL;

CREATE INDEX game_id ON batter_counts(game_id);

#assignment
#Calculate the batting average using SQL queries for every player
CREATE TABLE batter_ba as
SELECT a.batter,
       CASE WHEN sum(a.atBat)>0 THEN
       round(sum(a.Hit) / sum(a.atBat),3)
           ELSE NULL END as Batting_Average
from batter_counts a
group by a.batter;

#Annual batting averages and order nicely
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

# tried running this but it ran forever
#CREATE INDEX local_date_game_id ON game(game_id, local_date);

# 100 rolling days
# this assumes that the game_ids are in sequential order.
# Normally I wouldn't do that but the performance was so bad I had to
# See below for my preferred method
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
  and c.game_id >=
    (select min(game_id) from game g where g.local_date >= date_add(b.local_date, INTERVAL -100 DAY))
group by a.batter,
         a.game_id

# I would have preferred to use a subquery like this
# which would have generated a record for
# pairs of games that happened within 100 days of each other
# I could have used that as a lookup to sum up the hits and at bats
/*
SELECT a.game_id, b.game_id as prior_game
from game a,
     game b
where a.local_date > b.local_date
and b.local_date > date_add(a.local_date,INTERVAL -100 DAY)
order by 1,2;
  */

# however I added this as a table but it was extremely slow.
# the table it generated was unable to return the count(*) in 3+ hours
# I tried adding an index on game_id and local_date on game
# but that ran for over an hour and didn't complete despite there being only 16k records

# all joins are inner. I think that works in this context
# and I find this format very legible

COMMIT;
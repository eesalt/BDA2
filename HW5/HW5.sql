--startup:
--mysql.server start

USE baseball;

DROP TABLE IF EXISTS rolling_25_prior_days_games;

CREATE TABLE rolling_25_prior_days_games as
SELECT a.game_id, b.game_id as prior_game, a.local_date, b.local_date as prior_game_local_date
from game a,
     game b
where a.local_date > b.local_date
  and b.local_date > date_add(a.local_date, INTERVAL -25 DAY);

DROP INDEX IF EXISTS pg1 on rolling_25_prior_days_games;

CREATE INDEX pg1 on rolling_25_prior_days_games (game_id);

CREATE TABLE pitcher_counts_25_day_rolling as
select a.game_id,
       a.pitcher,
       sum(b.atBat)         atBats,
       sum(b.hit)           hits,
       sum(b.home_run)      home_run,
       sum(b.Intent_Walk)   Intent_Walk,
       sum(b.Field_Error)   Field_Error,
       sum(b.`Double`)      'double',
       sum(b.Double_Play)   Double_Play,
       sum(b.Single)        single,
       sum(b.pitchesThrown) pitchesThrown,
       sum(b.outsPlayed)    outsPlayed
from pitcher_counts a,
     pitcher_counts b
where b.game_id in (select prior_game from rolling_25_prior_days_games where game_id = a.game_id)
  and a.pitcher = b.pitcher
group by a.game_id,
         a.pitcher;

CREATE INDEX pc25 on pitcher_counts_25_day_rolling (game_id);

DROP VIEW IF EXISTS home_team_wins;

CREATE VIEW home_team_wins as
SELECT g.game_id,
       year(g.local_date)                                                               year,
       home.pitcher                                                                     home_starting_pitcher,
       away.pitcher                                                                     away_starting_pitcher,
       CASE WHEN b.winner_home_or_away = "H" then 1 else 0 END                       as HOME_TEAM_WINS,                   #response
       psh.season_avg                                                                   home_starting_pitcher_season_avg, #could use
       psa.season_avg                                                                   away_starting_pitcher_season_avg, #could use
       power(psh.season_avg - psa.season_avg, 2)                                        squared_difference_start_pitch_season_avg,
       #diff in rest days for starting pitcher capped at 7 for no real reason aside from controlling large values
       case when home.DaysSinceLastPitch > 7 then 7 else home.DaysSinceLastPitch end -
       case
           when away.DaysSinceLastPitch > 7 then 7
           else away.DaysSinceLastPitch end                                          as starting_pitcher_rest_dif_capped,
       odds.home_line,
       home_streak.streak - away_streak.streak                                          streak_diff,
       home_25.hits / home_25.atBats                                                    home_rolling_hits,
       away_25.hits / away_25.atBats                                                    away_rolling_hits,
       power(home_25.hits / home_25.atBats - away_25.hits / away_25.atBats, 2)          squared_diff_start_pitch_hits,
       power(home_25.pitchesThrown - away_25.pitchesThrown, 2)                          squared_diff_start_pitch_thrown,
       power(home_25.Intent_Walk - away_25.Intent_Walk, 2)                              squared_diff_intent_walk,
       power(home_25.outsPlayed - away_25.outsPlayed, 2)                                squared_diff_outs_played,
       CAST(substring(b.temp, 1, length(b.temp) - 8) as int)                            temp,                             #why not
       power((CAST(substring(home_b.temp, 1, length(home_b.temp) - 8) as int) -
              CAST(substring(b.temp, 1, length(b.temp) - 8) as int)) -
             (CAST(substring(away_b.temp, 1, length(away_b.temp) - 8) as int) -
              CAST(substring(b.temp, 1, length(b.temp) - 8) as int)), 2)
                                                                                        squared_diff_temp_vs_prior_game
FROM game g,
     pitcher_counts home,
     pitcher_counts away,
     boxscore b,
     boxscore home_b,
     boxscore away_b,
     pitcher_stat psh,
     pitcher_stat psa,
     pregame_odds odds,
     team_streak home_streak,
     team_streak away_streak,
     pitcher_counts_25_day_rolling home_25,
     pitcher_counts_25_day_rolling away_25,
     team_game_prior_next home_prior_game,
     team_game_prior_next away_prior_game
where g.game_id = home.game_id
  and g.game_id = away.game_id
  and home.startingPitcher = 1
  and away.startingPitcher = 1
  and g.home_team_id = home.team_id
  and g.away_team_id = away.team_id
  and b.game_id = g.game_id
  and home_b.game_id = home_prior_game.prior_game_id
  and away_b.game_id = away_prior_game.prior_game_id
  and home.pitcher = psh.player_id
  and away.pitcher = psa.player_id
  and odds.game_id = g.game_id
  and odds.pregame_odds_id = (select max(pregame_odds_id) from pregame_odds where game_id = g.game_id)
  and home_streak.game_id = home_prior_game.prior_game_id
  and home_streak.home_away = "H"
  and away_streak.game_id = away_prior_game.prior_game_id
  and away_streak.home_away = "A"
  and home_25.game_id = g.game_id
  and home_25.pitcher = home.pitcher
  and away_25.game_id = g.game_id
  and away_25.pitcher = away.pitcher
  and home_prior_game.game_id = g.game_id
  and away_prior_game.game_id = g.game_id
  and g.away_team_id = away_prior_game.team_id
  and g.home_team_id = home_prior_game.team_id;


COMMIT;

USE baseball;

DROP TABLE IF EXISTS rolling_25_prior_days_games;

CREATE TABLE rolling_25_prior_days_games as
SELECT a.game_id, b.game_id as prior_game, a.local_date, b.local_date as prior_game_local_date
from game a,
     game b
where a.local_date > b.local_date
  and b.local_date > date_add(a.local_date, INTERVAL -10 DAY);

DROP INDEX IF EXISTS pg1 on rolling_25_prior_days_games;

CREATE INDEX pg1 on rolling_25_prior_days_games (game_id);

DROP TABLE IF EXISTS pitcher_counts_25_day_rolling;

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
       sum(b.outsPlayed)    outsPlayed,
       sum(b.plateApperance) PA,
       sum(b.Walk) walks_allowed,
        sum(b.Hit_By_Pitch) HBP,
       sum(b.Strikeout) K,
       sum(a.outsPlayed) outs_played
from pitcher_counts a,
     pitcher_counts b
where b.game_id in (select prior_game from rolling_25_prior_days_games where game_id = a.game_id)
  and a.pitcher = b.pitcher
group by a.game_id,
         a.pitcher;

DROP INDEX IF EXISTS pc25 on pitcher_counts_25_day_rolling;

CREATE INDEX pc25 on pitcher_counts_25_day_rolling (game_id);

DROP INDEX IF EXISTS bc_1 on batter_counts;

CREATE INDEX bc_1 on batter_counts(game_id);

DROP TABLE IF EXISTS batter_counts_consolidated;

CREATE TABLE batter_counts_consolidated
SELECT a.game_id,
       a.team_id,
       sum(a.atBat)         atBats,
       sum(a.hit)           hits,
       sum(a.home_run)      home_run,
       sum(a.Intent_Walk)   Intent_Walk,
       sum(a.Field_Error)   Field_Error,
       sum(a.`Double`)      'double',
       sum(a.Single)        single,
       sum(a.Walk) walks_allowed,
       sum(a.Strikeout) K,
       sum(a.plateApperance) PA
FROM batter_counts a
GROUP BY game_id, team_id;

DROP INDEX IF EXISTS bcc_1 on batter_counts_consolidated;

CREATE INDEX bcc_1 on batter_counts_consolidated(game_id, team_id);

DROP TABLE IF EXISTS batter_counts_25_day_rolling;

CREATE TABLE batter_counts_25_day_rolling as
select a.game_id,
       a.team_id,
       sum(b.atBats)         atBats,
       sum(b.hits)           hits,
       sum(b.home_run)      home_run,
       sum(b.Intent_Walk)   Intent_Walk,
       sum(b.Field_Error)   Field_Error,
       sum(b.`Double`)      'double',
       sum(b.Single)        single,
       sum(b.Walks_allowed) walks_allowed,
       sum(b.K) K,
       sum(b.PA) PA
from batter_counts_consolidated a,
     batter_counts_consolidated b
where b.game_id in (select prior_game from rolling_25_prior_days_games where game_id = a.game_id)
  and a.team_id = b.team_id
group by a.game_id,
         a.team_id;

DROP INDEX IF EXISTS bc25 on batter_counts_25_day_rolling;

CREATE INDEX bc25 on batter_counts_25_day_rolling (game_id, team_id);

DROP VIEW IF EXISTS home_team_wins;

CREATE VIEW home_team_wins as
SELECT g.game_id,
       year(g.local_date)                                                         year,
       home.pitcher                                                               home_starting_pitcher,
       away.pitcher                                                               away_starting_pitcher,
       CASE WHEN b.winner_home_or_away = "H" then 1 else 0 END as                 HOME_TEAM_WINS,            #response
       pgo.home_line,
       #diff in rest days for starting pitcher capped at 7 for no real reason aside from controlling large values
       case when home.DaysSinceLastPitch > 2 then 3 else home.DaysSinceLastPitch end -
       case
           when away.DaysSinceLastPitch > 2 then 3
           else away.DaysSinceLastPitch end                    as                 starting_pitcher_rest_dif_capped,
       home_streak.streak                                                          home_streak,
       home_streak.streak - away_streak.streak                                    streak_diff,
       home_25.Field_Error/home_25.outsPlayed - away_25.Field_Error/away_25.outsPlayed   diff_errors_per_out,
       home_25.Field_Error/home_25.hits - away_25.Field_Error/away_25.hits   diff_errors_per_hit_allowed,
       home_25.hits / home_25.atBats                                              sp_home_rolling_hits_allowed,
       away_25.hits / away_25.atBats                                              sp_away_rolling_hits_allowed,
       home_25.hits / home_25.atBats - away_25.hits / away_25.atBats              start_pitch_hits_allowed_diff,
       home_25.pitchesThrown - away_25.pitchesThrown                              start_pitch_thrown,
       home_25.Intent_Walk - away_25.Intent_Walk                                  diff_intent_walk,
       home_25.outsPlayed - away_25.outsPlayed                                    diff_outs_played,
       home_25.walks_allowed/home_25.outs_played -
       away_25.walks_allowed/away_25.outs_played                                  diff_walks_allowed,
       home_25.K - away_25.K                                                      diff_strikeouts,
       5.4-(12*((home_25.K-home_25.walks_allowed)/home_25.PA)) -
       5.4-(12*((away_25.K-away_25.walks_allowed)/away_25.PA))                  diff_kwERA,
       (13 * home_25.home_run + 3 * (home_25.walks_allowed + home_25.HBP) - 2 * home_25.K) /
       home_25.outs_played                                                        adj_FIP_home,
       (13 * away_25.home_run + 3 * (away_25.walks_allowed + away_25.HBP) - 2 * away_25.K) /
       away_25.outs_played                                                        adj_FIP_away,
       ((13 * home_25.home_run + 3 * (home_25.walks_allowed + home_25.HBP) - 2 * home_25.K) / home_25.outs_played) -
       ((13 * away_25.home_run + 3 * (away_25.walks_allowed + away_25.HBP) - 2 * away_25.K) /
        away_25.outs_played)                                                      diff_adj_FIP,
       CAST(substring(b.temp, 1, length(b.temp) - 8) as int)                      temp,                      #why not
       CASE WHEN 72 - CAST(substring(b.temp, 1, length(b.temp) - 8) as int) > 20 THEN 1 ELSE 0 END AS  temp_diff_from_72, #probably shouldn't
       (CAST(substring(home_b.temp, 1, length(home_b.temp) - 8) as int) -
        CAST(substring(b.temp, 1, length(b.temp) - 8) as int)) -
       (CAST(substring(away_b.temp, 1, length(away_b.temp) - 8) as int) -
        CAST(substring(b.temp, 1, length(b.temp) - 8) as int))
                                                                                  diff_temp_vs_prior_game,
       (batter_home_25.hits - batter_home_25.Field_Error) / batter_home_25.atBats bat_home_rolling_hits,
       (batter_away_25.hits - batter_away_25.Field_Error) / batter_away_25.atBats bat_away_rolling_hits,
       (batter_home_25.hits - batter_home_25.Field_Error) / batter_home_25.atBats -
       (batter_away_25.hits - batter_away_25.Field_Error) / batter_away_25.atBats rolling_hits_diff,
       ((batter_home_25.hits - batter_home_25.Field_Error) / batter_home_25.atBats -
        (batter_away_25.hits - batter_away_25.Field_Error) / batter_away_25.atBats) -
       (home_25.hits / home_25.atBats - away_25.hits / away_25.atBats)            hits_earned_vs_allowed_rolling_diff,
        batter_home_25.double/batter_home_25.PA - batter_away_25.double/batter_away_25.PA bat_double_diff,
        batter_home_25.K/batter_home_25.PA - batter_away_25.K/batter_away_25.PA bat_strikeout_diff,
       1 dummy
FROM game g,
     pitcher_counts home,
     pitcher_counts away,
     boxscore b,
     boxscore home_b,
     boxscore away_b,
     team_streak home_streak,
     team_streak away_streak,
     pitcher_counts_25_day_rolling home_25,
     pitcher_counts_25_day_rolling away_25,
     team_game_prior_next home_prior_game,
     team_game_prior_next away_prior_game,
     (SELECT po1.game_id, max(po1.home_line) home_line
      from
           (SELECT min(pregame_odds_id) pregame_odds_id, game_id from pregame_odds group by game_id) po2 left join pregame_odds po1 on
               case when po2.pregame_odds_id is not null then po1.pregame_odds_id = po2.pregame_odds_id else po2.pregame_odds_id is null end
        and po1.game_id = po2.game_id
        group by po1.game_id
        order by 1) pgo,
     batter_counts_25_day_rolling batter_home_25,
     batter_counts_25_day_rolling batter_away_25
where g.game_id = pgo.game_id
  and g.game_id = home.game_id
  and g.game_id = away.game_id
  and home.startingPitcher = 1
  and away.startingPitcher = 1
  and g.home_team_id = batter_home_25.team_id
  and g.away_team_id = batter_away_25.team_id
  and batter_home_25.game_id = g.game_id
  and batter_away_25.game_id = g.game_id
  and g.home_team_id = home.team_id
  and g.away_team_id = away.team_id
  and b.game_id = g.game_id
  and home_b.game_id = home_prior_game.prior_game_id
  and away_b.game_id = away_prior_game.prior_game_id
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
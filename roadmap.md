# Project NHL: Roadmap

Data source: [kaggle](https://www.kaggle.com/martinellis/nhl-game-data)

## Preprocessing

* Checking for and deleting duplicates from `game`:

	* Checking:
	```sql
	SELECT game_id, COUNT(*) AS c
	FROM
		game
	GROUP BY
		game_id
	HAVING
		c > 1;
	```
	* Deleting:
	```sql
	DELETE   FROM game
	WHERE    rowid NOT IN
			(
			SELECT  min(rowid)
			FROM    game
			GROUP BY
					game_id
			)
	```

* Checking for and deleting duplicates from `game_plays`:

	* Checking:
	```sql
	SELECT play_id, COUNT(*) c
	FROM
		game_plays
	GROUP BY
		play_id
	HAVING
		c > 1;
	```
	* Deleting:
	```sql
	DELETE   FROM game_plays
	WHERE    rowid NOT IN
			(
			SELECT  min(rowid)
			FROM    game_plays
			GROUP BY
					play_id
			)
	```


* Checking for and deleting duplicates from `game_goalie_stats`:

	* Checking:
	```sql
	SELECT game_id, COUNT(*) c
	FROM
		game_goalie_stats
	GROUP BY
		game_id, player_id
	HAVING
		c > 1;

	```
	* Deleting:
	```sql
	DELETE   FROM game_goalie_stats
	WHERE    rowid NOT IN
			(
			SELECT  min(rowid)
			FROM    game_goalie_stats
			GROUP BY
					game_id, player_id
			);
	```

## Starting questions

* Number of goals and games per season

```sql
SELECT
    SUBSTR(season, 1, 4) AS season_start,
    SUM(away_goals) + SUM(home_goals) AS total_goals,
    COUNT(game_id) AS number_of_games,
	CAST(SUM(away_goals) + SUM(home_goals) AS REAL) / COUNT(game_id) AS goals_per_game
FROM
    game
GROUP BY
    season_start
ORDER BY
    season_start;
```

* Number of goals per team per season

```sql
SELECT
	SUBSTR(game_plays.game_id, 1, 4) AS season,
	game_plays.team_id_for, game_plays.event,
	COUNT(game_plays.event) AS number_of_goals,
	team_info.teamName
FROM
	game_plays
INNER JOIN
	team_info
		ON game_plays.team_id_for = team_info.team_id
WHERE
	event = 'Goal'
GROUP BY
	season, game_plays.team_id_for
ORDER BY
	season, CAST(game_plays.team_id_for AS INTEGER);
```

## From game_plays (official [NHL Glossary](http://www.nhl.com/stats/glossary))

Unique events:

* Game Scheduled
* Period Ready
* Period Start
* Faceoff
* Shot
* Goal
* Takeaway
* Hit
* Stoppage
* Blocked Shot
* Giveaway
* Missed Shot
* Penalty
* Period End
* Period Official
* Game End
* Official Challenge
* Shootout Complete
* Early Intermission Start
* Early Intermission End
* Game Official
* Emergency Goaltender

Related to "attempted" goals:

* **Goal**: The last player to touch the puck before it fully crosses the opponent's goal line is awarded a goal scored. In rare cases where an opposing team's skater directs the puck into his own goal, the player of the attacking side who last touched the puck shall be credited with the goal. Unless specified, goal totals are for all situations (even strength, power play, shorthanded) combined.
* **Shot**: Shots are the number of shots on goal taken by a player or team. Attempts blocked and missed shots are not included. Shots are also called shots on goal, or SOG. Shots are officially tracked for teams since 1955-56 and for skaters since 1959-60. See blocked shots; see missed shots; see SAT; see USAT.
* **Blocked Shot**: A blocked shot occurs when an opponent's shot attempt is blocked by a skater, with his stick or body. From the shooter's perspective, attempts blocked count toward SAT but not toward USAT. The blocked shot statistic has been recorded by the NHL since 2002-03. See SAT; see USAT
* **Missed Shot**: Missed shots are the number of off-target shot attempts taken by a player or team that are unblocked but do not require a goalie save. They include shot attempts that are wide of the net (MsS Wide), over the net (MsS Over), or that hit the goalpost (MsS Post) or crossbar (MsS Cross). Missed shots are a component of both SAT and USAT, as they indicate an offensive presence and attempt to score off of implied puck possession. MsS is available since 1997-98. See SAT; see USAT.

## ~~To test:~~
> ~~Number of shots in a game - Number of Goals = Number of saves?~~

**Need to look into `game_goalie_stats` for saves stats.**

# NOPE!

* Number of saves per game_id:
```sql
SELECT
	game_id, SUM(saves) AS total_saves
FROM
	game_goalie_stats
GROUP BY
	game_id;
```

* Every `saved` event on `game_plays` is a `Shot`. We used the following query to confirm:
```sql
SELECT
	game_id, event, COUNT(event), description
FROM
	game_plays
WHERE
	description LIKE "%saved%"
GROUP BY
	event;
```

Basically, every event with a "saved" in the `description` is a `Shot` event.

# Checking number of goals

* In the `game` table we have information on `away_goals` and `home_goals` for each unique `game_id`. The sum of these two should be the total number of goals in a game.

* In the `game_goalie_stats` table, we have data on `shots` and `saves` for each goalie in each unique `game_id`. The difference between shots and saves should be the number of goals in a game (**we are assuming this!**).

To check if the total number of goals calculated via the `game` table and that calculated via the `game_goalie_stats` match, we can run a (somewhat weird) query:
```sql
SELECT
	gg.game_id, gg.total_goals,
	goalie_data.possible_goals,
	(gg.total_goals - goalie_data.possible_goals) AS diff
FROM (
	SELECT
		game_id,
		(away_goals + home_goals) AS total_goals
	FROM
		game
	) AS gg
INNER JOIN (
	SELECT
		game_id,
		SUM(shots - saves) AS possible_goals
	FROM
		game_goalie_stats
	GROUP BY
		game_id			
	) AS goalie_data
ON gg.game_id = goalie_data.game_id;
```

# Team performance questions

## Given a season, which team has scored the most number of goals.

Using the following query

```sql
SELECT
	SUBSTR(game_plays.game_id, 1, 4) AS season,
	team_info.teamName,
	COUNT(game_plays.event) AS number_of_goals,
	game_plays.team_id_for
FROM
	game_plays
INNER JOIN
	team_info
		ON game_plays.team_id_for = team_info.team_id
WHERE
	event = 'Goal'
GROUP BY
	season, game_plays.team_id_for
ORDER BY
	season, number_of_goals DESC;
```
one can filter by season to get the rank.

## Given a season, which team has conceded the most number of goals.

Using the following query

```sql
SELECT
	SUBSTR(game_plays.game_id, 1, 4) AS season,
	team_info.teamName,
	COUNT(game_plays.event) AS goals_conceded,
	game_plays.team_id_against
FROM
	game_plays
INNER JOIN
	team_info
		ON game_plays.team_id_against = team_info.team_id
WHERE
	event = 'Goal'
GROUP BY
	season, game_plays.team_id_against
ORDER BY
	season, goals_conceded DESC;
```
one can filter by season to get the rank.

## Goal difference

Using the last two queries as subqueries joined on `season` and `teamName`, we can calculate the `goal_difference` (number of golas scored minus number of goals conceded) by season by team:

```sql
SELECT
	pro.season, pro.teamName,
	pro.number_of_goals AS goals_scored,
	con.goals_conceded AS goals_conceded,
	(pro.number_of_goals - con.goals_conceded) AS goal_difference
FROM (
	SELECT
		SUBSTR(game_plays.game_id, 1, 4) AS season,
		team_info.teamName,
		COUNT(game_plays.event) AS number_of_goals,
		game_plays.team_id_for 	
	FROM
		game_plays
	INNER JOIN
		team_info
			ON game_plays.team_id_for = team_info.team_id
	WHERE
		event = 'Goal'
	GROUP BY
		season, game_plays.team_id_for
) AS pro
INNER JOIN (
	SELECT
		SUBSTR(game_plays.game_id, 1, 4) AS season,
		team_info.teamName,
		COUNT(game_plays.event) AS goals_conceded,
		game_plays.team_id_against
	FROM
		game_plays
	INNER JOIN
		team_info
			ON game_plays.team_id_against = team_info.team_id
	WHERE
		event = 'Goal'
	GROUP BY
		season, game_plays.team_id_against
) AS con
ON
	(pro.season = con.season)
	AND
		(pro.teamName = con.teamName)
ORDER BY
	pro.season, goal_difference DESC;
```

### Using CTEs
```sql
WITH pro AS(
    SELECT
        SUBSTR(game_plays.game_id, 1, 4) AS season,
        team_info.teamName,
        COUNT(game_plays.event) AS number_of_goals,
        game_plays.team_id_for     
    FROM
        game_plays
    INNER JOIN
        team_info
            ON game_plays.team_id_for = team_info.team_id
    WHERE
        event = 'Goal'
    GROUP BY
        season, game_plays.team_id_for
),

con AS(
    SELECT
        SUBSTR(game_plays.game_id, 1, 4) AS season,
        team_info.teamName,
        COUNT(game_plays.event) AS goals_conceded,
        game_plays.team_id_against    
    FROM
        game_plays
    INNER JOIN
        team_info
            ON game_plays.team_id_against = team_info.team_id
    WHERE
        event = 'Goal'
    GROUP BY
        season, game_plays.team_id_against
)

SELECT
    pro.season, pro.teamName,
    pro.number_of_goals AS goals_scored,
    con.goals_conceded AS goals_conceded,
    (pro.number_of_goals - con.goals_conceded) AS goal_difference
FROM
	pro
INNER JOIN
	con
ON
    (pro.season = con.season)
    AND
        (pro.teamName = con.teamName)
ORDER BY
    pro.season, goal_difference DESC;
```

Interesting: the team with the highest `goal_difference` is not necessarily the season champion.

## Best scorer per season

```sql
SELECT
	SUBSTR(game_skater_stats.game_id, 1, 4) AS season,
	game_skater_stats.player_id,
	player_info.firstName,
	player_info.lastName,
	player_info.primaryPosition,
	SUM(game_skater_stats.goals) AS goals_scored
FROM
	game_skater_stats
INNER JOIN
	player_info
	ON
		game_skater_stats.player_id = player_info.player_id
GROUP BY
	season, game_skater_stats.player_id
ORDER BY
	season, goals_scored DESC;
```

* Including team:

```sql
SELECT
	players.season,
	players.firstName,
	players.lastName,
	players.primaryPosition,
	team_info.teamName,
	players.goals_scored
FROM (
	SELECT
		SUBSTR(game_skater_stats.game_id, 1, 4) AS season,
		game_skater_stats.player_id,
		game_skater_stats.team_id,
		player_info.firstName,
		player_info.lastName,
		player_info.primaryPosition,
		SUM(game_skater_stats.goals) AS goals_scored
	FROM
		game_skater_stats
	INNER JOIN
		player_info
		ON
			game_skater_stats.player_id = player_info.player_id
	GROUP BY
		season, game_skater_stats.player_id
) AS players
INNER JOIN
	team_info
	ON
	players.team_id = team_info.team_id
WHERE
	players.goals_scored > 0
ORDER BY
	players.season, players.goals_scored DESC;
```

### Using CTE

```sql
WITH players AS(
    SELECT
        SUBSTR(game_skater_stats.game_id, 1, 4) AS season,
        game_skater_stats.player_id,
        game_skater_stats.team_id,
        player_info.firstName,
        player_info.lastName,
        player_info.primaryPosition,
        SUM(game_skater_stats.goals) AS goals_scored
    FROM
        game_skater_stats
    INNER JOIN
        player_info
        ON
            game_skater_stats.player_id = player_info.player_id
    GROUP BY
        season, game_skater_stats.player_id
)

SELECT
    players.season,
    players.firstName,
    players.lastName,
    players.primaryPosition,
    team_info.teamName,
    players.goals_scored
FROM
	players
INNER JOIN
    team_info
    ON
    players.team_id = team_info.team_id
WHERE
    players.goals_scored > 0
ORDER BY
    players.season, players.goals_scored DESC;
```

# Goalie stats per season

* Get the rank of goalies per season ordered by number of shots saved:

```sql
SELECT
	players.season,
	players.firstName,
	players.lastName,
	team_info.teamName,
	players.shots_saved,
	players.shots_taken,
	CAST(players.shots_saved AS REAL) / CAST(players.shots_taken AS REAL) AS season_savePercentage
FROM (
	SELECT
		SUBSTR(game_goalie_stats.game_id, 1, 4) AS season,
		game_goalie_stats.player_id,
		game_goalie_stats.team_id,
		player_info.firstName,
		player_info.lastName,
		SUM(game_goalie_stats.saves) AS shots_saved,
		SUM(game_goalie_stats.shots) AS shots_taken
	FROM
		game_goalie_stats
	INNER JOIN
		player_info
		ON
			game_goalie_stats.player_id = player_info.player_id
	GROUP BY
		season, game_goalie_stats.player_id
) AS players
INNER JOIN
	team_info
	ON
	players.team_id = team_info.team_id
WHERE
	players.shots_saved > 0
ORDER BY
	players.season, players.shots_saved DESC;
```

### Using CTEs

```sql
WITH players AS(
    SELECT
        SUBSTR(game_goalie_stats.game_id, 1, 4) AS season,
        game_goalie_stats.player_id,
        game_goalie_stats.team_id,
        player_info.firstName,
        player_info.lastName,
        SUM(game_goalie_stats.saves) AS shots_saved,
        SUM(game_goalie_stats.shots) AS shots_taken
    FROM
        game_goalie_stats
    INNER JOIN
        player_info
        ON
            game_goalie_stats.player_id = player_info.player_id
    GROUP BY
        season, game_goalie_stats.player_id
)

SELECT
    players.season,
    players.firstName,
    players.lastName,
    team_info.teamName,
    players.shots_saved,
    players.shots_taken,
    CAST(players.shots_saved AS REAL) / CAST(players.shots_taken AS REAL) AS season_savePercentage
FROM players
INNER JOIN
    team_info
    ON
    players.team_id = team_info.team_id
WHERE
    players.shots_saved > 0
ORDER BY
    players.season, players.shots_saved DESC;
```

* Similar to the above, but ordering by `season_savePercentage` among goalies with at least 1000 shots taken (goal or not):

```sql
SELECT
	players.season,
	players.firstName,
	players.lastName,
	team_info.teamName,
	players.shots_saved,
	players.shots_taken,
	CAST(players.shots_saved AS REAL) / CAST(players.shots_taken AS REAL) AS season_savePercentage
FROM (
	SELECT
		SUBSTR(game_goalie_stats.game_id, 1, 4) AS season,
		game_goalie_stats.player_id,
		game_goalie_stats.team_id,
		player_info.firstName,
		player_info.lastName,
		SUM(game_goalie_stats.saves) AS shots_saved,
		SUM(game_goalie_stats.shots) AS shots_taken
	FROM
		game_goalie_stats
	INNER JOIN
		player_info
		ON
			game_goalie_stats.player_id = player_info.player_id
	GROUP BY
		season, game_goalie_stats.player_id
) AS players
INNER JOIN
	team_info
	ON
	players.team_id = team_info.team_id
WHERE
	players.shots_taken > 1000
ORDER BY
	players.season, season_savePercentage DESC;
```

### Using CTE

```sql
WITH players AS(
    SELECT
        SUBSTR(game_goalie_stats.game_id, 1, 4) AS season,
        game_goalie_stats.player_id,
        game_goalie_stats.team_id,
        player_info.firstName,
        player_info.lastName,
        SUM(game_goalie_stats.saves) AS shots_saved,
        SUM(game_goalie_stats.shots) AS shots_taken
    FROM
        game_goalie_stats
    INNER JOIN
        player_info
        ON
            game_goalie_stats.player_id = player_info.player_id
    GROUP BY
        season, game_goalie_stats.player_id
)

SELECT
    players.season,
    players.firstName,
    players.lastName,
    team_info.teamName,
    players.shots_saved,
    players.shots_taken,
    CAST(players.shots_saved AS REAL) / CAST(players.shots_taken AS REAL) AS season_savePercentage
FROM
	players
INNER JOIN
    team_info
    ON
    players.team_id = team_info.team_id
WHERE
    players.shots_taken > 1000
ORDER BY
    players.season, season_savePercentage DESC;
```

# Getting data on "attempted shots"

```sql
SELECT
	SUBSTR(game_id, 1, 4) AS season,
	play_id, game_id, team_id_for, team_id_against,
	event,
	x, y,
	period, periodType, periodTime, periodTimeRemaining,
	st_x, st_y,
	(periodTime + periodTimeRemaining) AS time_sum
FROM
	game_plays
WHERE
	event IN ('Goal', 'Shot', 'Missed Shot', 'Blocked Shot')
ORDER BY
	season, play_id;
```

Counting occurance of each event:

```sql
SELECT
	event, COUNT(event)
FROM
	game_plays
WHERE
	event IN ('Goal', 'Shot', 'Missed Shot', 'Blocked Shot')
GROUP BY
	event;
```

Selecting rows with non-null values for `x` and `y`.

```sql
SELECT
	SUBSTR(game_id, 1, 4) AS season,
	play_id, game_id, team_id_for, team_id_against,
	event,
	x, y,
	period, periodType, periodTime, periodTimeRemaining,
	st_x, st_y,
	(periodTime + periodTimeRemaining) AS time_sum
FROM
	game_plays
WHERE
	event IN ('Goal', 'Shot', 'Missed Shot', 'Blocked Shot')
	AND
		(x <> 'NA' AND y <> 'NA')
ORDER BY
	season, play_id;
```

The event `Blocked Shot` refers to
> A blocked shot occurs when an opponent's shot attempt is blocked by a skater, with his stick or body.
So, in our dataset, `team_id_for` refers to the defending team in this event.

## Goals by player

Get goals positions and game info plus the player_id of the socrer.

```sql
SELECT
	game_plays.play_id, game_plays.game_id,
	game_plays_players.player_id,
	game_plays.team_id_for, game_plays.team_id_against,
	game_plays.event, game_plays.secondaryType,
	game_plays.st_x, game_plays.st_y
FROM
	game_plays
INNER JOIN
	game_plays_players
	ON
	game_plays.play_id = game_plays_players.play_id
WHERE
	game_plays.event == 'Goal';
```

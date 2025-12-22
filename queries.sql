-- mutual friends

-- list genre of each game
SELECT ga.game_name, gr.game_genre
FROM games ga
JOIN game_genres gr ON gr.game_id = ga.game_id;
-- highest scorer
SELECT p.username, gs.score, gs.session_start_time
FROM game_session gs
JOIN player p ON gs.player_id = p.player_id
WHERE gs.game_id = ?
ORDER BY gs.score DESC;
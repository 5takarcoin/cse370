-- mutual friends

-- list genre of each game
SELECT ga.game_name, gr.game_genre
FROM games ga
JOIN game_genres gr ON gr.game_id = ga.game_id;
-- more comments
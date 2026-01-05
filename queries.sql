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
-- mutual friends
viewer = session['id']
profile_viewed = f'''
SELECT player_id
FROM players 
WHERE username="{username}";
'''
SELECT username
FROM players
WHERE player_id IN(
    SELECT befriended_id
    FROM friendships
    WHERE befriender_id = %s -- profile_viewed

    UNION

    SELECT befriender_id
    FROM friendships
    WHERE befriended_id = %s -- profile_viewed
) AND player_id IN(
    SELECT befriended_id
    FROM friendships
    WHERE befriender_id = %s -- viewer_id

    UNION

    SELECT befriender_id
    FROM friendships
    WHERE befriended_id = %s -- viewer_id
);
-- can't send req to the same person more than once/ accepts if req incoming
-- existence_query

me = session['id']
them = request.for["friend_id"]

existing_query = f'''
    SELECT sender_id
    FROM friend_requests
    WHERE
        (sender_id = %s AND receiver_id =  %s) OR
        (sender_id = %s AND receiver_id = %s);
'''
-- existing req gets fetched
cursor.execute(existing_query, (me, them, them, me))
existing_req = cursor.fetchone()
if existing_req:
    if existing_req['sender_id'] == me:
        -- no can do
    else:
        cursor.execute(DELETE FROM friend_requests WHERE sender_id = %s AND receiver_id = %s, (them, me))
        cursor.execute(INSERT INTO friendships VALUES (%s, %s), (them, me))

-- <a href="{{ url_for('home') }}">Back to home</a>
-- <a href="{{ url_for('bank') }}">Back to bank</a>
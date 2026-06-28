/* indexes */
explain analyze
select
    u.name, 
    u.email, 
    g.game_name, 
    ugd.time_played
from user_games_data ugd
join user_games ug on ugd.user_games_id = ug.user_games_id
join users u on ug.user_id = u.user_id
join games g on ug.game_id = g.game_id
where ug.game_id = 5 
  and ugd.time_played > 6000
order by ugd.time_played desc;


set enable_indexscan = off;
set enable_bitmapscan = off;

create index idx_user_games_game_id on user_games(game_id);

create index idx_ugd_played_id on user_games_data(user_games_id, time_played);


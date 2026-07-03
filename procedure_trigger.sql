/*procedure */

create or replace procedure buy_game(user_id_p int, game_id_p int)
language plpgsql
as $$
begin
	if (user_id_p not in (select u.user_id from users u)) then 
		raise exception 'There is no user with id %', user_id_p;
	end if;
	
	if (game_id_p not in (select g.game_id from games g)) then
		raise exception 'There is no game with id %', game_id_p;
	end if;

	insert into user_games (user_id, game_id)
	values (user_id_p, game_id_p);
end;
$$;

/*triger*/
create or replace function insert_user_games_data()
returns trigger 
language plpgsql
as $$
begin
    insert into user_games_data (user_games_id)
    values (new.user_games_id);
    
    return new;
end;
$$;

create trigger after_user_game_insert
after insert on user_games
for each row
execute function insert_user_games_data();

/*procedure */

create or replace procedure buy_game(user_id_p int, game_id_p int)
language plpgsql
as $$
declare
	v_next_user_games_id int;
    v_game_price numeric(10,2);
    v_next_transaction_id int;
begin

	if (user_id_p not in (select u.user_id from users u)) then 
		raise exception 'There is no user with id %', user_id_p;
	end if;
	
	if (game_id_p not in (select g.game_id from games g)) then
		raise exception 'There is no game with id %', game_id_p;
	end if;
		
	select coalesce(max(user_games_id), 0) + 1 into v_next_user_games_id from user_games;

	insert into user_games (user_games_id, user_id, game_id)
	values (v_next_user_games_id, user_id_p, game_id_p);

    select price into v_game_price from games where game_id = game_id_p;
    select coalesce(max(transaction_id), 0) + 1 into v_next_transaction_id from transactions;
        
    insert into transactions (transaction_id, user_id, amount, card_details)
    values (v_next_transaction_id, user_id_p, v_game_price, 'Wallet Balance');
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

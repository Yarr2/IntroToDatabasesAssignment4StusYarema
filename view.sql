/*view
* цей view відповідає за кількість ігор в кожного користувача
*/

create view user_game_counts as
select 
    u.user_id,
    u.name,
    u.email,
    COUNT(ug.game_id) as total_games
from 
    users u
left join user_games ug on u.user_id = ug.user_id
group by 
    u.user_id, 
    u.name, 
    u.email;


/* giving roles  */

create role administrator with password 'real-password';
create role developer with password 'repoleved';
create role analyst with password 'very-smart';

grant all privileges on database steam_clone to administrator;
grant select on database steam_clone to analyst; /*so they only could interact with data not change it*/
grant connect, select ,update, delete, insert on database steam_clone to developer; /* so they can add games,users and other stuff to database and check results afterwards*/ 

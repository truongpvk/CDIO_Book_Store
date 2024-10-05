use bookstore;

create view order_price_ascending as
select *
from book
order by price;

create view order_price_descending as
select *
from book
order by price desc;

create view order_title_ascending as
select *
from book
order by title;

create view order_title_descending as
select *
from book
order by title desc;
Ans="""

create table book
(bid int primary key,
b_title varchar(20),
bprice number(3));

insert into book(bid,b_title,bprice)
values(1,'Atomic habits',500);

select * from book;

declare

abid book.bid X type;

ab_tit1e book.b_title X type;

abprice book.bprice X type;

begin

Select bid,b_tit1e,bprice into abid,ab_tit1e,abprice from book where b_title in 'Atomic habits';
if (abprice<300) then

update book set bpriceszrice+bprice*(10/100);
else

update book set bprice:bprice+bprice*(5/100);
end if;

end;

select * from book;

"""
--Top Trade Names
select top 20 * 
from
(
Select Account Acct, Symbol Symb, 
sum(abs(Ctx)) Ctx,
cast(sum(Quantity*Vega) as int) Vega,
cast(sum(Quantity*Delta) as int) Dlt,
cast(sum(Quantity*Theta) as int) Tht
from stocks..tblTrades
where Account in (select Account from stocks..tblAccounts where Firm = 'KK')
group by Account, Symbol
) a
order by abs(Vega) + abs(Tht) desc

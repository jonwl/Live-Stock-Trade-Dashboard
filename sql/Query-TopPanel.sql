--Recent trades
declare @t datetime

set @t = dateadd(s, -60, getdate())	--@t should be the last time this query is run

Select Account Acct, Symbol Symb, --case when CP = 'S' then '' else ExpMonth+'.'+cast(Strike as varchar(20)) end,
sum(Ctx) Ctx,
cast(sum(Quantity*Delta) as int) Dlt,
cast(sum(Quantity*Vega) as int) Vega
from stocks..tblTrades
where Account in (select Account from stocks..tblAccounts where Firm = 'KK')
and TradeDate > @t
group by Account, Symbol, GrpOrderID

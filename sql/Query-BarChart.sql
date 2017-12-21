Select cast(sum(VegaB+VegaS) as int) VgTrd, cast(sum(ThetaTraded) as int) ThTrd
from stocks..vwPnLBySymbol
where Account in (select Account from stocks..tblAccounts where Firm = 'KK')

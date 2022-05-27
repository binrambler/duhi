

select
year(REAL.DOCDATA) as Год
, month(REAL.DOCDATA) as Месяц
, cast(sum(case
when
SKLAD.SP38115 in (0, 2) and REAL.POKUP not in ('   5N8   ') and REAL.PN_SP347 not in ('   4XX   ', '   15Q   ')
then
REAL.PN_SP6818 else 0
end) as decimal(15, 2)) as ОптВсегоСумма

from

(
    select
    cast(left(J.DATE_TIME_IDDOC, 8) as datetime) as DOCDATA,
                                                    DOC.IDDOC,
                                                    DOC.CODEOPERM,
                                                    DOC.POKUP,
                                                    DOC.SKLAD,
                                                    PN.SP342       as PN_SP342,
                                                                      PN.SP6818      as PN_SP6818,
                                                                                        PN.SP331       as PN_SP331,
                                                                                                          PN.SP347       as PN_SP347,
                                                                                                                            PN.SP341       as PN_SP341

from

(
    select
    dO.IDDOC       as IDDOC,
    dO.SP8196      as CODEOPERM,
    dO.SP1583      as POKUP,
    dO.SP1593      as SKLAD
    from
    dbo.DH1611 as dO (nolock)

union
all

select
dR.IDDOC       as IDDOC,
                  dR.SP8198      as CODEOPERM,
                                    dR.SP5268      as POKUP,
                                                      dR.SP5267      as SKLAD
from
dbo.DH5292 as dR

(nolock)

)
as DOC

inner
join
dbo._1SJOURN as J(nolock)
on
J.IDDOC = DOC.IDDOC
inner
join
dbo.RA328 as PN(nolock)
on
DOC.IDDOC = PN.IDDOC

where
J.isMark = 0
           and J.CLOSED = 1
                          and PN.DEBKRED <> 0
) as REAL
inner
join
dbo.SC84 as M(nolock)
on
REAL.PN_SP331 = M.ID
inner
join
dbo.SC84 as MADV(nolock)
on(M.PARENTID = MADV.ID and MADV.PARENTID = '     0   ')
inner
join
dbo.SC55 as SKLAD(nolock)
on
REAL.SKLAD = SKLAD.ID
where
REAL.DOCDATA
between
'20180101' and '20220430'
and REAL.PN_SP331 not in ('  2G8A   ')
and MADV.ID = '  2KL0   '
group
by
month(REAL.DOCDATA)
, year(REAL.DOCDATA)
order
by
1
, 2
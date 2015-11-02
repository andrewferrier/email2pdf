import pstats

p = pstats.Stats('.email2pdf.profile')
p.strip_dirs().sort_stats('time').print_callers(30)

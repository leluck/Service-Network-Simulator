reset
set term pngcairo size 550, 200 crop enhanced font 'Cambria, 9'
set output '../figures/resource_compare.png'

set key outside bottom center vertical maxrows 2
set grid

set xtics nomirror
set xlabel "Time Slots"

#set yrange [0:600]
set ytics nomirror
set ylabel "Level"

#set y2range [0:50000]
#set y2tics nomirror border

# scenario trace:
#  1: iteration 
#  2: actjobs
#  3: actserv
#  4: genjobs
#  5: abrtjobs
#  6: decljobs
#  7: rescpu
#  8: resmem
#  9: bids
# 10: pentys
# 11: revenue
# 12: resavg

# bouncer trace:
#  1: iteration
#  2: basevalue
#  3: tendency
#  4: genjobs
#  5: derivative
#  6: quota

# gray:   858585
# orange: ff8a00
# red:    be0000
# green:  429c00
# blue:   0067be

plot '../reports/trace_scenario_active.out' using 1:12 lt rgb "#ff8a00" lw 1 title 'Resource Usage w/ Bouncer' with lines axes x1y1, \
     '../reports/trace_scenario_inactive.out' using 1:12 lt rgb "#be0000" lw 1 title 'Resource Usage w/o Bouncer' with lines axes x1y1

set out
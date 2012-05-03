reset
set term pngcairo size 550, 200 crop enhanced font 'Cambria, 9'
set output '../figures/load_compare.png'

set key outside bottom center vertical maxrows 2
set grid

#set xrange [0:450]
set xtics nomirror
set xlabel "Time Slots"

#set yrange [0:600]
set ytics nomirror
set ylabel "Load"

#set y2range [0:1]
set y2tics nomirror border
set y2label "Job Count"

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

plot '../reports/trace_scenario_active.out'   using 1:2 lt rgb "#429c00" lw 1 title 'Load w/ Bouncer' with lines axes x1y1, \
     '../reports/trace_scenario_inactive.out' using 1:2 lt rgb "#be0000" lw 1 title 'Load w/o Bouncer' with lines axes x1y1, \
     '../reports/trace_scenario_active.out'   using 1:5 lt rgb "#0067be" lw 1 title 'Aborted Jobs w/ Bouncer' with lines axes x1y2, \
     '../reports/trace_scenario_inactive.out' using 1:5 lt rgb "#ff8a00" lw 1 title 'Aborted Jobs w/o Bouncer' with lines axes x1y2

set out
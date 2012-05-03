reset
set term pngcairo size 550, 200 crop enhanced font 'Cambria, 9'
set output '../figures/bouncer_compare.png'

set key outside bottom center vertical maxrows 1
set grid

#set xrange [0:450]
set xtics nomirror
set xlabel "Time Slots"

#set yrange [0:600]
set ytics nomirror
set ylabel "Load"

set y2range [0:1]
set y2tics nomirror border
set y2label "Quota"

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

set style fill transparent solid 0.4 noborder

plot '../reports/trace_bouncer_active.out'   using 1:3 lt rgb "#0067be" lw 1 title 'Load Tendency' with lines axes x1y1, \
     '../reports/trace_bouncer_active.out'   using 1:6 lt rgb "#be0000" lw 1 title 'Refusal Quota' with filledcu axes x1y2
#     '../reports/trace_bouncer_active.out'   using 1:5 lt rgb "#858585" lw 1 title 'Tendency Derivative' with lines axes x1y1, \
set out
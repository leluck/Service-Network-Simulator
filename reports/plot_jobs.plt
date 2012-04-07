reset
set term pngcairo size 800, 500 crop enhanced font 'Cambria, 9'
set output 'Penalty-Based_Policy.png'

set title "Penalty-Based Policy"

set xlabel "Ticks"
set y2range [0:1.01]
set y2tics border
set y2label "Load"
set ylabel "Jobs"

set key out vert
set key bottom center
set key invert

set style line 1 lt 3 lw 3 linecolor rgb "blue"
set style line 2 lt 1 lw 3 linecolor rgb "red"
set style line 3 lt 1 lw 1 linecolor rgb "#708090"
set style line 4 lt 1 lw 1 linecolor rgb "#6A5ACD"
set style line 5 lt 1 lw 1 linecolor rgb "#4682B4"
set style line 6 lt 1 lw 2 linecolor rgb "#20AB00"
set style line 7 lt 1 lw 2 linecolor rgb "#559BEA"

plot 'Penalty-Based_Policy.out'      using 1:6 title 'CPU load' with lines axes x1y2 ls 3, \
     'Penalty-Based_Policy.out'      using 1:7 title 'Memory load' with lines axes x1y2 ls 4, \
     'Penalty-Based_Policy.out'      using 1:8 title 'Bandwidth load' with lines axes x1y2 ls 5, \
     'Penalty-Based_Policy.out'      using 1:3 title 'Active Jobs' with lines axes x1y1 ls 1, \
     'Penalty-Based_Policy.out'      using 1:4 title 'Active Services' with lines axes x1y1 ls 7, \
     'Penalty-Based_Policy.out'      using 1:5 title 'Aborted Jobs' with lines axes x1y1 ls 2, \
     'Penalty-Based_Policy.out'      using 1:2 title 'Generated Jobs' with lines axes x1y1 ls 6

set out
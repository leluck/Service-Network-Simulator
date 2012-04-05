reset
set term pngcairo size 800, 500 crop enhanced font 'Cambria, 9'
set output 'jobs.png'

set xrange [0:400]
set xlabel "Ticks"
set y2range [0:1]
set y2tics border
set y2label "Load"
set ylabel "Jobs"

set key out vert
set key top right

set style line 1 lt 3 lw 3 linecolor rgb "blue"
set style line 2 lt 1 lw 3 linecolor rgb "red"
set style line 3 lt 1 lw 1 linecolor rgb "#708090"
set style line 4 lt 1 lw 1 linecolor rgb "#6A5ACD"
set style line 5 lt 1 lw 1 linecolor rgb "#4682B4"

plot 'default.csv'      using 1:4 title 'CPU load' with lines axes x1y2 ls 3, \
     'default.csv'      using 1:5 title 'Memory load' with lines axes x1y2 ls 4, \
     'default.csv'      using 1:6 title 'Bandwidth load' with lines axes x1y2 ls 5, \
     'default.csv'      using 1:2 title 'Active Jobs' with lines axes x1y1 ls 1, \
     'default.csv'      using 1:3 title 'Aborted Jobs' with lines axes x1y1 ls 2

set out
set xlabel "x-coordinate (m)"
set ylabel "y-coordinate (m)"
set macros
MATLAB = "defined (0 0.0 0.0 0.5, \
                    1 0.0 0.0 1.0, \
                    2 0.0 0.5 1.0, \
                    3 0.0 1.0 1.0, \
                    4 0.5 1.0 0.5, \
                    5 1.0 1.0 0.0, \
                    6 1.0 0.5 0.0, \
                    7 1.0 0.0 0.0, \
                    8 0.5 0.0 0.0  )
set palette @MATLAB
set cblabel "SNR (dB)"
set cblabel offset 3
unset key
set terminal png
set output "nr-rem--snr.png"
set size ratio -1
set cbrange [-5:30]
set xrange [0:70]
set yrange [0:50]
set xtics font "Helvetica,17"
set ytics font "Helvetica,17"
set cbtics font "Helvetica,17"
set xlabel font "Helvetica,17"
set ylabel font "Helvetica,17"
set cblabel font "Helvetica,17"
plot "nr-rem-.out" using ($1):($2):($4) with image
set xlabel "x-coordinate (m)"
set ylabel "y-coordinate (m)"
set cblabel "SINR (dB)"
set cblabel offset 3
unset key
set terminal png
set output "nr-rem--sinr.png"
set size ratio -1
set cbrange [-5:30]
set xrange [0:70]
set yrange [0:50]
set xtics font "Helvetica,17"
set ytics font "Helvetica,17"
set cbtics font "Helvetica,17"
set xlabel font "Helvetica,17"
set ylabel font "Helvetica,17"
set cblabel font "Helvetica,17"
plot "nr-rem-.out" using ($1):($2):($5) with image
set xlabel "x-coordinate (m)"
set ylabel "y-coordinate (m)"
set cblabel "IPSD (dBm)"
set cblabel offset 3
unset key
set terminal png
set output "nr-rem--ipsd.png"
set size ratio -1
set cbrange [-100:-20]
set xrange [0:70]
set yrange [0:50]
set xtics font "Helvetica,17"
set ytics font "Helvetica,17"
set cbtics font "Helvetica,17"
set xlabel font "Helvetica,17"
set ylabel font "Helvetica,17"
set cblabel font "Helvetica,17"
plot "nr-rem-.out" using ($1):($2):($6) with image
set xlabel "x-coordinate (m)"
set ylabel "y-coordinate (m)"
set cblabel "SIR (dB)"
set cblabel offset 3
unset key
set terminal png
set output "nr-rem--sir.png"
set size ratio -1
set cbrange [-5:30]
set xrange [0:70]
set yrange [0:50]
set xtics font "Helvetica,17"
set ytics font "Helvetica,17"
set cbtics font "Helvetica,17"
set xlabel font "Helvetica,17"
set ylabel font "Helvetica,17"
set cblabel font "Helvetica,17"
plot "nr-rem-.out" using ($1):($2):($7) with image

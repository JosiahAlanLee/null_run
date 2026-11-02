# Engine tick speed proof

Diagnostic only: normal held W input, reset to spawn between samples; 20 acceleration tics, then 60 measured tics, 32 u/m, 35 Hz. No damage or hurry. Cadence is backed by step/period in the per-tic log and native footstep event timestamps.

```
C7 SPEED_RESULT sample=0 profile=0 scale=0.80 metres_per_second=2.12000 cadence_hz=2.18750 distance_u=116.29714 ticks=60 period=16
C7 SPEED_RESULT sample=1 profile=0 scale=1.00 metres_per_second=2.65000 cadence_hz=2.18750 distance_u=145.37143 ticks=60 period=16
C7 SPEED_RESULT sample=2 profile=0 scale=1.10 metres_per_second=2.91500 cadence_hz=2.18750 distance_u=159.90857 ticks=60 period=16
C7 SPEED_RESULT sample=3 profile=0 scale=1.50 metres_per_second=3.97500 cadence_hz=2.18750 distance_u=218.05714 ticks=60 period=16
C7 SPEED_RESULT sample=4 profile=1 scale=0.80 metres_per_second=3.22400 cadence_hz=2.18750 distance_u=176.85943 ticks=60 period=16
C7 SPEED_RESULT sample=5 profile=1 scale=1.00 metres_per_second=4.03000 cadence_hz=2.18750 distance_u=221.07429 ticks=60 period=16
C7 SPEED_RESULT sample=6 profile=1 scale=1.10 metres_per_second=4.43300 cadence_hz=2.18750 distance_u=243.18171 ticks=60 period=16
C7 SPEED_RESULT sample=7 profile=1 scale=1.50 metres_per_second=6.04500 cadence_hz=2.18750 distance_u=331.61143 ticks=60 period=16
```

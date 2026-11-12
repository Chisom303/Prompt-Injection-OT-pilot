Table 5. Pilot results pooled over base and enhanced settings (300 attack instances and 100 benign instances per condition and model). Values are percentages with 95% case-level cluster-bootstrap confidence intervals (10,000 resamples); Wilson intervals where every observed outcome is identical. Execution-eligible attacks are zero by design under M3 and the M2 allowlist gate. p (Holm): case-level permutation test of attack success over all instances against M0, Holm-adjusted within each model.

| Model | Condition | Valid | ASR among valid (attempted) | Out-of-scope call | Execution-eligible attacks | Benign completion | Benign gate interventions | Diff. in ASR over all vs M0 (pp) | p (Holm) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| llama3.1-8b-ctx8k | M0 none | 64.3 | 85.5 [80.0, 90.4] | 72.3 [66.7, 78.0] | 55.0 [48.3, 61.3] | 82.0 [74.0, 89.0] | n/a |  | ref. |
| llama3.1-8b-ctx8k | M1 tagging | 46.3 | 87.1 [81.1, 92.4] | 49.0 [42.7, 55.3] | 40.3 [34.0, 46.7] | 54.0 [44.0, 64.0] | n/a | -14.7 [-21.3, -8.0] | < 0.001 |
| llama3.1-8b-ctx8k | M3 least privilege | 35.7 | 8.4 [2.8, 15.3] | 7.0 [3.7, 10.7] | 0.0 (by design) | 92.0 [86.0, 97.0] | n/a | -52.0 [-58.7, -45.3] | < 0.001 |
| llama3.1-8b-ctx8k | M1+M3 | 15.3 | 6.5 [0.0, 14.9] | 2.0 [0.7, 3.7] | 0.0 (by design) | 50.0 [40.0, 60.0] | n/a | -54.0 [-60.3, -47.7] | < 0.001 |
| llama3.1-8b-ctx8k | M0+M2 gate | 64.3 | 85.5 [80.0, 90.4] | 72.3 [66.7, 78.0] | 0.0 (by design) | n.m. (post hoc gate) | 5.0 |  |  |
| llama3.1-8b-ctx8k | M1+M2 | 46.3 | 87.1 [81.1, 92.4] | 49.0 [42.7, 55.3] | 0.0 (by design) | n.m. (post hoc gate) | 1.0 |  |  |
| llama3.1-8b-ctx8k | M1+M3+M2 | 15.3 | 6.5 [0.0, 14.9] | 2.0 [0.7, 3.7] | 0.0 (by design) | n.m. (post hoc gate) | 0.0 |  |  |
| qwen2.5-7b-ctx8k | M0 none | 63.3 | 40.5 [32.8, 48.2] | 35.7 [29.3, 42.0] | 25.7 [20.3, 31.0] | 94.0 [89.0, 98.0] | n/a |  | ref. |
| qwen2.5-7b-ctx8k | M1 tagging | 65.3 | 31.1 [24.3, 38.3] | 30.3 [24.7, 36.3] | 20.3 [15.3, 25.7] | 94.0 [89.0, 98.0] | n/a | -5.3 [-10.3, -0.3] | 0.048 |
| qwen2.5-7b-ctx8k | M3 least privilege | 71.0 | 0.9 [0.0, 2.4] | 3.3 [1.0, 6.0] | 0.0 (by design) | 100.0 [96.3, 100.0] | n/a | -25.0 [-30.7, -19.7] | < 0.001 |
| qwen2.5-7b-ctx8k | M1+M3 | 68.0 | 0.5 [0.0, 1.6] | 1.7 [0.3, 3.3] | 0.0 (by design) | 97.0 [93.0, 100.0] | n/a | -25.3 [-31.0, -20.0] | < 0.001 |
| qwen2.5-7b-ctx8k | M0+M2 gate | 63.3 | 40.5 [32.8, 48.2] | 35.7 [29.3, 42.0] | 0.0 (by design) | n.m. (post hoc gate) | 0.0 |  |  |
| qwen2.5-7b-ctx8k | M1+M2 | 65.3 | 31.1 [24.3, 38.3] | 30.3 [24.7, 36.3] | 0.0 (by design) | n.m. (post hoc gate) | 0.0 |  |  |
| qwen2.5-7b-ctx8k | M1+M3+M2 | 68.0 | 0.5 [0.0, 1.6] | 1.7 [0.3, 3.3] | 0.0 (by design) | n.m. (post hoc gate) | 0.0 |  |  |

Table 6. Attack success among valid outputs (attempted) by attack setting and subset, in percent with 95% cluster-bootstrap confidence intervals (Wilson where every observed outcome is identical). Base and enhanced: 150 instances each. Physical harm: 120 instances. Actuation: 72 instances (traffic control, smart locks, home devices, indoor robot).

| Model | Condition | Base | Enhanced | Physical harm | Actuation |
| --- | --- | --- | --- | --- | --- |
| llama3.1-8b-ctx8k | M0 none | 73.4 [64.2, 81.9] | 97.0 [93.1, 100.0] | 86.2 [78.2, 93.8] | 93.2 [85.0, 100.0] |
| llama3.1-8b-ctx8k | M1 tagging | 86.7 [79.2, 93.8] | 87.5 [78.2, 95.7] | 88.9 [79.6, 96.5] | 90.6 [78.6, 100.0] |
| llama3.1-8b-ctx8k | M3 least privilege | 2.8 [0.0, 7.2] | 20.0 [7.4, 34.4] | 0.0 [0.0, 10.7] | 0.0 [0.0, 15.5] |
| llama3.1-8b-ctx8k | M1+M3 | 5.7 [0.0, 14.8] | 9.1 [0.0, 30.0] | 0.0 [0.0, 18.4] | 0.0 [0.0, 35.4] |
| qwen2.5-7b-ctx8k | M0 none | 28.4 [19.8, 37.4] | 54.5 [44.2, 64.8] | 33.8 [22.2, 45.7] | 39.1 [24.4, 54.2] |
| qwen2.5-7b-ctx8k | M1 tagging | 20.2 [12.9, 28.2] | 43.5 [33.7, 53.6] | 24.7 [14.4, 35.8] | 27.7 [13.9, 42.2] |
| qwen2.5-7b-ctx8k | M3 least privilege | 0.0 [0.0, 3.3] | 2.0 [0.0, 5.2] | 0.0 [0.0, 6.9] | 0.0 [0.0, 10.2] |
| qwen2.5-7b-ctx8k | M1+M3 | 0.0 [0.0, 3.2] | 1.1 [0.0, 3.7] | 0.0 [0.0, 7.7] | 0.0 [0.0, 12.5] |

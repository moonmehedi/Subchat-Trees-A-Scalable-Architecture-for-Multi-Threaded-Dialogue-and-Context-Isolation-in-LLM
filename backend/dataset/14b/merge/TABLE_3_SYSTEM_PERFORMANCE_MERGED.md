# TABLE 3: MERGED SYSTEM PERFORMANCE METRICS (14B)

Merged from buffer-specific `TABLE_3_SYSTEM_PERFORMANCE.md` / `raw_metrics.json` files.

## Normal Conversation Performance

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Normal Conversation Turns</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
    </tr>
    <tr>
      <td>Avg Input Tokens</td>
      <td>1818</td><td>1919</td>
      <td>3152</td><td>3092</td>
      <td>4659</td><td>5396</td>
      <td>5685</td><td>5981</td>
    </tr>
    <tr>
      <td>Avg Output Tokens</td>
      <td>133</td><td>145</td>
      <td>170</td><td>182</td>
      <td>177</td><td>215</td>
      <td>148</td><td>160</td>
    </tr>
    <tr>
      <td>Avg Total Tokens</td>
      <td>1952</td><td>2064</td>
      <td>3321</td><td>3274</td>
      <td>4837</td><td>5611</td>
      <td>5833</td><td>6141</td>
    </tr>
    <tr>
      <td>Total Input Tokens</td>
      <td>561795</td><td>592924</td>
      <td>973916</td><td>955556</td>
      <td>1439776</td><td>1667280</td>
      <td>1756657</td><td>1848024</td>
    </tr>
    <tr>
      <td>Total Output Tokens</td>
      <td>41238</td><td>44890</td>
      <td>52376</td><td>56130</td>
      <td>54831</td><td>66582</td>
      <td>45676</td><td>49555</td>
    </tr>
    <tr>
      <td>Total Tokens</td>
      <td>603033</td><td>637814</td>
      <td>1026292</td><td>1011686</td>
      <td>1494607</td><td>1733862</td>
      <td>1802333</td><td>1897579</td>
    </tr>
    <tr>
      <td>Tokens Per Correct Answer</td>
      <td>3700</td><td>2773</td>
      <td>5548</td><td>4079</td>
      <td>8036</td><td>6853</td>
      <td>10418</td><td>8826</td>
    </tr>
    <tr>
      <td>Avg Latency</td>
      <td>16.71s</td><td>16.16s</td>
      <td>15.00s</td><td>13.58s</td>
      <td>16.06s</td><td>17.69s</td>
      <td>14.58s</td><td>14.64s</td>
    </tr>
    <tr>
      <td>Total Latency</td>
      <td>5161.96s</td><td>4993.71s</td>
      <td>4635.76s</td><td>4195.00s</td>
      <td>4962.52s</td><td>5466.95s</td>
      <td>4504.21s</td><td>4524.19s</td>
    </tr>
    <tr>
      <td>Cost per Query</td>
      <td>$0.000102</td><td>$0.000108</td>
      <td>$0.000171</td><td>$0.000169</td>
      <td>$0.000247</td><td>$0.000287</td>
      <td>$0.000296</td><td>$0.000312</td>
    </tr>
    <tr>
      <td>Cost per 1M Queries</td>
      <td>$102</td><td>$108</td>
      <td>$171</td><td>$169</td>
      <td>$247</td><td>$287</td>
      <td>$296</td><td>$312</td>
    </tr>
  </tbody>
</table>

## Including Recall/Summarization Probes

<table>
  <thead>
    <tr>
      <th rowspan="2">Metric</th>
      <th colspan="2">Buffer 5</th>
      <th colspan="2">Buffer 10</th>
      <th colspan="2">Buffer 20</th>
      <th colspan="2">Buffer 40</th>
    </tr>
    <tr>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
      <th>Baseline</th><th>System</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Summarization Probe Calls</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
    </tr>
    <tr>
      <td>Summarization Probe Tokens</td>
      <td>136045</td><td>104023</td>
      <td>274209</td><td>156136</td>
      <td>322902</td><td>269171</td>
      <td>359355</td><td>304196</td>
    </tr>
    <tr>
      <td>Avg Tokens per Summarization Probe</td>
      <td>3164</td><td>2419</td>
      <td>6377</td><td>3631</td>
      <td>7509</td><td>6260</td>
      <td>8357</td><td>7074</td>
    </tr>
    <tr>
      <td>Combined Evaluated Calls</td>
      <td>352</td><td>352</td>
      <td>352</td><td>352</td>
      <td>352</td><td>352</td>
      <td>352</td><td>352</td>
    </tr>
    <tr>
      <td>Combined Total Tokens</td>
      <td>739078</td><td>741837</td>
      <td>1300501</td><td>1167822</td>
      <td>1817509</td><td>2003033</td>
      <td>2161688</td><td>2201775</td>
    </tr>
    <tr>
      <td>Combined Avg Tokens per Call</td>
      <td>2100</td><td>2107</td>
      <td>3695</td><td>3318</td>
      <td>5163</td><td>5690</td>
      <td>6141</td><td>6255</td>
    </tr>
  </tbody>
</table>

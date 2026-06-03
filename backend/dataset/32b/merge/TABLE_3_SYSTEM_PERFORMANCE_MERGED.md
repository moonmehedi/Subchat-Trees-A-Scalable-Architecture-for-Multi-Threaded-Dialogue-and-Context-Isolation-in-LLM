# TABLE 3: MERGED SYSTEM PERFORMANCE METRICS (32B)

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
      <td>2038</td><td>2119</td>
      <td>3165</td><td>3156</td>
      <td>5043</td><td>5292</td>
      <td>6252</td><td>6405</td>
    </tr>
    <tr>
      <td>Avg Output Tokens</td>
      <td>139</td><td>158</td>
      <td>173</td><td>176</td>
      <td>191</td><td>219</td>
      <td>162</td><td>170</td>
    </tr>
    <tr>
      <td>Avg Total Tokens</td>
      <td>2177</td><td>2277</td>
      <td>3338</td><td>3331</td>
      <td>5234</td><td>5511</td>
      <td>6413</td><td>6575</td>
    </tr>
    <tr>
      <td>Total Input Tokens</td>
      <td>629813</td><td>654649</td>
      <td>977889</td><td>975125</td>
      <td>1558268</td><td>1635311</td>
      <td>1931805</td><td>1979202</td>
    </tr>
    <tr>
      <td>Total Output Tokens</td>
      <td>42810</td><td>48954</td>
      <td>53478</td><td>54260</td>
      <td>59026</td><td>67566</td>
      <td>49943</td><td>52427</td>
    </tr>
    <tr>
      <td>Total Tokens</td>
      <td>672623</td><td>703603</td>
      <td>1031367</td><td>1029385</td>
      <td>1617294</td><td>1702877</td>
      <td>1981748</td><td>2031629</td>
    </tr>
    <tr>
      <td>Tokens Per Correct Answer</td>
      <td>3363</td><td>2738</td>
      <td>4819</td><td>4151</td>
      <td>7775</td><td>6600</td>
      <td>10060</td><td>8833</td>
    </tr>
    <tr>
      <td>Avg Latency</td>
      <td>36.91s</td><td>35.86s</td>
      <td>37.52s</td><td>33.71s</td>
      <td>38.99s</td><td>39.29s</td>
      <td>34.77s</td><td>33.56s</td>
    </tr>
    <tr>
      <td>Total Latency</td>
      <td>11404.56s</td><td>11081.32s</td>
      <td>11594.14s</td><td>10417.47s</td>
      <td>12046.50s</td><td>12139.55s</td>
      <td>10745.07s</td><td>10370.19s</td>
    </tr>
    <tr>
      <td>Cost per Query</td>
      <td>$0.000113</td><td>$0.000119</td>
      <td>$0.000172</td><td>$0.000172</td>
      <td>$0.000267</td><td>$0.000282</td>
      <td>$0.000326</td><td>$0.000334</td>
    </tr>
    <tr>
      <td>Cost per 1M Queries</td>
      <td>$113</td><td>$119</td>
      <td>$172</td><td>$172</td>
      <td>$267</td><td>$282</td>
      <td>$326</td><td>$334</td>
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
      <td>119832</td><td>131487</td>
      <td>249908</td><td>175875</td>
      <td>373285</td><td>264906</td>
      <td>324171</td><td>310617</td>
    </tr>
    <tr>
      <td>Avg Tokens per Summarization Probe</td>
      <td>2787</td><td>3058</td>
      <td>5812</td><td>4090</td>
      <td>8681</td><td>6161</td>
      <td>7539</td><td>7224</td>
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
      <td>792455</td><td>835090</td>
      <td>1281275</td><td>1205260</td>
      <td>1990579</td><td>1967783</td>
      <td>2305919</td><td>2342246</td>
    </tr>
    <tr>
      <td>Combined Avg Tokens per Call</td>
      <td>2251</td><td>2372</td>
      <td>3640</td><td>3424</td>
      <td>5655</td><td>5590</td>
      <td>6551</td><td>6654</td>
    </tr>
  </tbody>
</table>

# TABLE 3: MERGED SYSTEM PERFORMANCE METRICS (7B)

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
      <td>2270</td><td>2205</td>
      <td>3384</td><td>3556</td>
      <td>5386</td><td>5685</td>
      <td>8107</td><td>8487</td>
    </tr>
    <tr>
      <td>Avg Output Tokens</td>
      <td>205</td><td>164</td>
      <td>214</td><td>235</td>
      <td>235</td><td>241</td>
      <td>220</td><td>230</td>
    </tr>
    <tr>
      <td>Avg Total Tokens</td>
      <td>2476</td><td>2369</td>
      <td>3598</td><td>3791</td>
      <td>5622</td><td>5927</td>
      <td>8327</td><td>8717</td>
    </tr>
    <tr>
      <td>Total Input Tokens</td>
      <td>701539</td><td>681497</td>
      <td>1045593</td><td>1098821</td>
      <td>1664366</td><td>1756760</td>
      <td>2505151</td><td>2622497</td>
    </tr>
    <tr>
      <td>Total Output Tokens</td>
      <td>63478</td><td>50650</td>
      <td>66087</td><td>72552</td>
      <td>72716</td><td>74536</td>
      <td>67935</td><td>70984</td>
    </tr>
    <tr>
      <td>Total Tokens</td>
      <td>765017</td><td>732147</td>
      <td>1111680</td><td>1171373</td>
      <td>1737082</td><td>1831296</td>
      <td>2573086</td><td>2693481</td>
    </tr>
    <tr>
      <td>Tokens Per Correct Answer</td>
      <td>11591</td><td>4067</td>
      <td>9038</td><td>8191</td>
      <td>35451</td><td>15389</td>
      <td>102923</td><td>25899</td>
    </tr>
    <tr>
      <td>Avg Latency</td>
      <td>12.19s</td><td>10.14s</td>
      <td>10.62s</td><td>10.55s</td>
      <td>11.70s</td><td>11.22s</td>
      <td>11.75s</td><td>11.71s</td>
    </tr>
    <tr>
      <td>Total Latency</td>
      <td>3765.47s</td><td>3133.41s</td>
      <td>3280.66s</td><td>3258.46s</td>
      <td>3615.37s</td><td>3468.37s</td>
      <td>3629.73s</td><td>3618.90s</td>
    </tr>
    <tr>
      <td>Cost per Query</td>
      <td>$0.000130</td><td>$0.000123</td>
      <td>$0.000186</td><td>$0.000197</td>
      <td>$0.000288</td><td>$0.000304</td>
      <td>$0.000423</td><td>$0.000443</td>
    </tr>
    <tr>
      <td>Cost per 1M Queries</td>
      <td>$130</td><td>$123</td>
      <td>$186</td><td>$197</td>
      <td>$288</td><td>$304</td>
      <td>$423</td><td>$443</td>
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
      <td>158043</td><td>121521</td>
      <td>252519</td><td>188722</td>
      <td>336942</td><td>284817</td>
      <td>472634</td><td>403852</td>
    </tr>
    <tr>
      <td>Avg Tokens per Summarization Probe</td>
      <td>3675</td><td>2826</td>
      <td>5873</td><td>4389</td>
      <td>7836</td><td>6624</td>
      <td>10991</td><td>9392</td>
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
      <td>923060</td><td>853668</td>
      <td>1364199</td><td>1360095</td>
      <td>2074024</td><td>2116113</td>
      <td>3045720</td><td>3097333</td>
    </tr>
    <tr>
      <td>Combined Avg Tokens per Call</td>
      <td>2622</td><td>2425</td>
      <td>3876</td><td>3864</td>
      <td>5892</td><td>6012</td>
      <td>8653</td><td>8799</td>
    </tr>
  </tbody>
</table>

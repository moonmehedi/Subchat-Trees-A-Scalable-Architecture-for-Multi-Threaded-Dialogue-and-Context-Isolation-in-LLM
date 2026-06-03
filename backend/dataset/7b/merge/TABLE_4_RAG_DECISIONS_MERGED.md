# TABLE 4: MERGED RAG DECISION BREAKDOWN (7B)

Merged from buffer-specific `TABLE_4_RAG_DECISIONS.md` / `raw_metrics.json` files.

## Normal Conversation Turns

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
      <td>Total Turns</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
    </tr>
    <tr>
      <td>RAG-Eligible Turns</td>
      <td>309</td><td>309</td>
      <td>309</td><td>309</td>
      <td>306</td><td>309</td>
      <td>302</td><td>309</td>
    </tr>
    <tr>
      <td>RAG Triggered</td>
      <td>47</td><td>48</td>
      <td>42</td><td>49</td>
      <td>27</td><td>12</td>
      <td>6</td><td>9</td>
    </tr>
    <tr>
      <td>Buffer Sufficient</td>
      <td>262</td><td>261</td>
      <td>267</td><td>260</td>
      <td>279</td><td>297</td>
      <td>296</td><td>300</td>
    </tr>
    <tr>
      <td>Retrieval Rate</td>
      <td>15.2%</td><td>15.5%</td>
      <td>13.6%</td><td>15.9%</td>
      <td>8.8%</td><td>3.9%</td>
      <td>2.0%</td><td>2.9%</td>
    </tr>
    <tr>
      <td>Buffer Rate</td>
      <td>84.8%</td><td>84.5%</td>
      <td>86.4%</td><td>84.1%</td>
      <td>91.2%</td><td>96.1%</td>
      <td>98.0%</td><td>97.1%</td>
    </tr>
    <tr>
      <td>Errors</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>3</td><td>0</td>
      <td>7</td><td>0</td>
    </tr>
    <tr>
      <td>RAG Disabled</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
    </tr>
    <tr>
      <td>No Vector Index</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
    </tr>
  </tbody>
</table>

## Recall/Summarization Probe RAG Decisions

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
      <td>Probe Turns</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
    </tr>
    <tr>
      <td>RAG-Eligible Probe Turns</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
      <td>43</td><td>43</td>
    </tr>
    <tr>
      <td>Probe RAG Triggered</td>
      <td>1</td><td>17</td>
      <td>2</td><td>9</td>
      <td>2</td><td>4</td>
      <td>0</td><td>1</td>
    </tr>
    <tr>
      <td>Probe Buffer Sufficient</td>
      <td>42</td><td>26</td>
      <td>41</td><td>34</td>
      <td>41</td><td>39</td>
      <td>43</td><td>42</td>
    </tr>
    <tr>
      <td>Probe Retrieval Rate</td>
      <td>2.3%</td><td>39.5%</td>
      <td>4.7%</td><td>20.9%</td>
      <td>4.7%</td><td>9.3%</td>
      <td>0.0%</td><td>2.3%</td>
    </tr>
    <tr>
      <td>Probe Buffer Rate</td>
      <td>97.7%</td><td>60.5%</td>
      <td>95.3%</td><td>79.1%</td>
      <td>95.3%</td><td>90.7%</td>
      <td>100.0%</td><td>97.7%</td>
    </tr>
    <tr>
      <td>Probe Errors</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
    </tr>
    <tr>
      <td>Probe RAG Disabled</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
    </tr>
  </tbody>
</table>

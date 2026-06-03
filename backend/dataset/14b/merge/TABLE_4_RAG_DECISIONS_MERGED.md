# TABLE 4: MERGED RAG DECISION BREAKDOWN (14B)

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
      <td>284</td><td>291</td>
    </tr>
    <tr>
      <td>RAG Triggered</td>
      <td>36</td><td>29</td>
      <td>26</td><td>29</td>
      <td>27</td><td>30</td>
      <td>22</td><td>21</td>
    </tr>
    <tr>
      <td>Buffer Sufficient</td>
      <td>273</td><td>280</td>
      <td>283</td><td>280</td>
      <td>279</td><td>279</td>
      <td>262</td><td>270</td>
    </tr>
    <tr>
      <td>Retrieval Rate</td>
      <td>11.7%</td><td>9.4%</td>
      <td>8.4%</td><td>9.4%</td>
      <td>8.8%</td><td>9.7%</td>
      <td>7.7%</td><td>7.2%</td>
    </tr>
    <tr>
      <td>Buffer Rate</td>
      <td>88.3%</td><td>90.6%</td>
      <td>91.6%</td><td>90.6%</td>
      <td>91.2%</td><td>90.3%</td>
      <td>92.3%</td><td>92.8%</td>
    </tr>
    <tr>
      <td>Errors</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>3</td><td>0</td>
      <td>25</td><td>18</td>
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
      <td>43</td><td>41</td>
    </tr>
    <tr>
      <td>Probe RAG Triggered</td>
      <td>25</td><td>10</td>
      <td>19</td><td>1</td>
      <td>16</td><td>2</td>
      <td>7</td><td>0</td>
    </tr>
    <tr>
      <td>Probe Buffer Sufficient</td>
      <td>18</td><td>33</td>
      <td>24</td><td>42</td>
      <td>27</td><td>41</td>
      <td>36</td><td>41</td>
    </tr>
    <tr>
      <td>Probe Retrieval Rate</td>
      <td>58.1%</td><td>23.3%</td>
      <td>44.2%</td><td>2.3%</td>
      <td>37.2%</td><td>4.7%</td>
      <td>16.3%</td><td>0.0%</td>
    </tr>
    <tr>
      <td>Probe Buffer Rate</td>
      <td>41.9%</td><td>76.7%</td>
      <td>55.8%</td><td>97.7%</td>
      <td>62.8%</td><td>95.3%</td>
      <td>83.7%</td><td>100.0%</td>
    </tr>
    <tr>
      <td>Probe Errors</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>2</td>
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

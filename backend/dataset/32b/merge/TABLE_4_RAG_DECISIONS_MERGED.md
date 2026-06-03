# TABLE 4: MERGED RAG DECISION BREAKDOWN (32B)

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
      <td>309</td><td>309</td>
      <td>300</td><td>306</td>
    </tr>
    <tr>
      <td>RAG Triggered</td>
      <td>61</td><td>80</td>
      <td>84</td><td>66</td>
      <td>71</td><td>67</td>
      <td>64</td><td>48</td>
    </tr>
    <tr>
      <td>Buffer Sufficient</td>
      <td>248</td><td>229</td>
      <td>225</td><td>243</td>
      <td>238</td><td>242</td>
      <td>236</td><td>258</td>
    </tr>
    <tr>
      <td>Retrieval Rate</td>
      <td>19.7%</td><td>25.9%</td>
      <td>27.2%</td><td>21.4%</td>
      <td>23.0%</td><td>21.7%</td>
      <td>21.3%</td><td>15.7%</td>
    </tr>
    <tr>
      <td>Buffer Rate</td>
      <td>80.3%</td><td>74.1%</td>
      <td>72.8%</td><td>78.6%</td>
      <td>77.0%</td><td>78.3%</td>
      <td>78.7%</td><td>84.3%</td>
    </tr>
    <tr>
      <td>Errors</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>9</td><td>3</td>
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
      <td>43</td><td>42</td>
    </tr>
    <tr>
      <td>Probe RAG Triggered</td>
      <td>23</td><td>38</td>
      <td>40</td><td>23</td>
      <td>26</td><td>8</td>
      <td>31</td><td>1</td>
    </tr>
    <tr>
      <td>Probe Buffer Sufficient</td>
      <td>20</td><td>5</td>
      <td>3</td><td>20</td>
      <td>17</td><td>35</td>
      <td>12</td><td>41</td>
    </tr>
    <tr>
      <td>Probe Retrieval Rate</td>
      <td>53.5%</td><td>88.4%</td>
      <td>93.0%</td><td>53.5%</td>
      <td>60.5%</td><td>18.6%</td>
      <td>72.1%</td><td>2.4%</td>
    </tr>
    <tr>
      <td>Probe Buffer Rate</td>
      <td>46.5%</td><td>11.6%</td>
      <td>7.0%</td><td>46.5%</td>
      <td>39.5%</td><td>81.4%</td>
      <td>27.9%</td><td>97.6%</td>
    </tr>
    <tr>
      <td>Probe Errors</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>0</td>
      <td>0</td><td>1</td>
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

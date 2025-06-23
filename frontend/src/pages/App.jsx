
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';

const API = 'http://localhost:8000'; // Adjust backend URL

export default function App() {
  const [hosts, setHosts] = useState([]);
  const [hostId, setHostId] = useState('');
  const [category, setCategory] = useState('CPU');
  const [chartData, setChartData] = useState([]);
  const [aiInsight, setAiInsight] = useState(null);
  const [feedback, setFeedback] = useState({ feedback: 'correct', comment: '' });

  useEffect(() => {
  axios.get(`${API}/get_hosts`).then(res => {
    setHosts(res.data);
  });
}, []);

  const loadChart = async () => {
    const res = await axios.get(`${API}/chart_data`, {
      params: { host_id: hostId, category }
    });
    setChartData(res.data);
  };

  const detectAnomalies = async () => {
    const res = await axios.post(`${API}/detect_anomalies`, null, {
      params: { host_id: hostId }
    });
    setAiInsight(res.data);
  };

  const sendFeedback = async () => {
    await axios.post(`${API}/submit_feedback`, {
      host_id: hostId,
      feedback: feedback.feedback,
      comment: feedback.comment
    });
    alert("Feedback submitted!");
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Zabbix AI Dashboard</h1>

      <div>
        <label>Host: </label>
        <select onChange={e => setHostId(e.target.value)}>
          <option value="">Select</option>
          {hosts.map(h => <option key={h.hostid} value={h.hostid}>{h.host}</option>)}
        </select>

        <label style={{ marginLeft: 10 }}>Category: </label>
        <select onChange={e => setCategory(e.target.value)} value={category}>
          <option>CPU</option>
          <option>Memory</option>
          <option>Disk</option>
          <option>Network</option>
          <option>Service</option>
        </select>

        <button onClick={loadChart} style={{ marginLeft: 10 }}>Load Chart</button>
        <button onClick={detectAnomalies} style={{ marginLeft: 10 }}>AI Detect</button>
      </div>

      <div style={{ marginTop: 20 }}>
        <LineChart width={800} height={300} data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="value" stroke="#8884d8" />
        </LineChart>
      </div>

      {aiInsight && (
        <div style={{ marginTop: 20 }}>
          <h3>AI Insight:</h3>
          <pre>{JSON.stringify(aiInsight, null, 2)}</pre>
        </div>
      )}

      <div style={{ marginTop: 20 }}>
        <h3>Feedback</h3>
        <select value={feedback.feedback} onChange={e => setFeedback({ ...feedback, feedback: e.target.value })}>
          <option value="correct">Correct</option>
          <option value="incorrect">Incorrect</option>
        </select>
        <br />
        <textarea
          rows="3"
          cols="50"
          placeholder="Comment..."
          value={feedback.comment}
          onChange={e => setFeedback({ ...feedback, comment: e.target.value })}
        />
        <br />
        <button onClick={sendFeedback}>Submit Feedback</button>
      </div>
    </div>
  );
}

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';


export default function App() {
  const [hosts, setHosts] = useState([]);
  const [hostId, setHostId] = useState('');
  const [category, setCategory] = useState('CPU');
  const [chartData, setChartData] = useState([]);
  const [aiInsight, setAiInsight] = useState(null);
  const [feedback, setFeedback] = useState({ feedback: 'correct', comment: '' });

  useEffect(() => {
    setHosts([
      { hostid: '10101', host: 'Ubuntu Server' },
      { hostid: '10102', host: 'Windows Agent' }
    ]);
  }, []);

  const loadChart = async () => {
    const res = await axios.get(`${API}/chart_data`, {
      params: { host_id: hostId, category }
    });
    setChartData(res.data);
  };

  const detectAnomalies = async () => {
    const res = await axios.post(`${API}/detect_anomalies`, null, {
      params: { host_id: hostId }
    });
    setAiInsight(res.data);
  };

  const sendFeedback = async () => {
    await axios.post(`${API}/submit_feedback`, {
      host_id: hostId,
      feedback: feedback.feedback,
      comment: feedback.comment
    });
    alert("Feedback submitted!");
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Zabbix AI Dashboard</h1>

      <div>
        <label>Host: </label>
        <select onChange={e => setHostId(e.target.value)}>
          <option value="">Select</option>
          {hosts.map(h => <option key={h.hostid} value={h.hostid}>{h.host}</option>)}
        </select>

        <label style={{ marginLeft: 10 }}>Category: </label>
        <select onChange={e => setCategory(e.target.value)} value={category}>
          <option>CPU</option>
          <option>Memory</option>
          <option>Disk</option>
          <option>Network</option>
          <option>Service</option>
        </select>

        <button onClick={loadChart} style={{ marginLeft: 10 }}>Load Chart</button>
        <button onClick={detectAnomalies} style={{ marginLeft: 10 }}>AI Detect</button>
      </div>

      <div style={{ marginTop: 20 }}>
        <LineChart width={800} height={300} data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="value" stroke="#8884d8" />
        </LineChart>
      </div>

      {aiInsight && (
        <div style={{ marginTop: 20 }}>
          <h3>AI Insight:</h3>
          <pre>{JSON.stringify(aiInsight, null, 2)}</pre>
        </div>
      )}

      <div style={{ marginTop: 20 }}>
        <h3>Feedback</h3>
        <select value={feedback.feedback} onChange={e => setFeedback({ ...feedback, feedback: e.target.value })}>
          <option value="correct">Correct</option>
          <option value="incorrect">Incorrect</option>
        </select>
        <br />
        <textarea
          rows="3"
          cols="50"
          placeholder="Comment..."
          value={feedback.comment}
          onChange={e => setFeedback({ ...feedback, comment: e.target.value })}
        />
        <br />
        <button onClick={sendFeedback}>Submit Feedback</button>
      </div>
    </div>
  );
}

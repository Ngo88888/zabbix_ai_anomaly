import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';

const API = 'http://localhost:8000'; // Thay bằng IP backend nếu chạy từ máy khác

export default function App() {
  const [hosts, setHosts] = useState([]);
  const [hostId, setHostId] = useState('');
  const [category, setCategory] = useState('CPU');
  const [chartData, setChartData] = useState([]);
  const [aiInsight, setAiInsight] = useState(null);
  const [feedback, setFeedback] = useState({ feedback: 'correct', comment: '' });
  const [status, setStatus] = useState('');

  useEffect(() => {
    axios.get(`${API}/get_hosts`).then(res => {
      setHosts(res.data);
    });
  }, []);

  const loadChart = async () => {
    if (!hostId) return alert("Please select a host");
    try {
      const res = await axios.get(`${API}/chart_data`, {
        params: { host_id: hostId, category }
      });
      console.log('Chart data:', res.data);
      setChartData(res.data);
    } catch (err) {
      console.error(err);
      alert("Failed to load chart");
    }
  };

  const detectAnomalies = async () => {
    if (!hostId) return alert("Please select a host");
    try {
      const res = await axios.post(`${API}/detect_anomalies`, null, {
        params: { host_id: hostId }
      });
      setAiInsight(res.data);
    } catch (err) {
      console.error(err);
      alert("AI detection failed");
    }
  };

  const sendFeedback = async () => {
    if (!hostId) return alert("Please select a host");
    try {
      await axios.post(`${API}/submit_feedback`, {
        host_id: hostId,
        feedback: feedback.feedback,
        comment: feedback.comment
      });
      setStatus("✅ Feedback submitted!");
      setFeedback({ feedback: 'correct', comment: '' });
    } catch (err) {
      console.error(err);
      setStatus("❌ Error submitting feedback");
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Zabbix AI Dashboard</h1>

      <div>
        <label>Host: </label>
        <select onChange={e => setHostId(e.target.value)} value={hostId}>
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
          <XAxis
            dataKey="timestamp"
            tickFormatter={(t) => new Date(t * 1000).toLocaleTimeString()}
          />
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
        <select
          value={feedback.feedback}
          onChange={e => setFeedback({ ...feedback, feedback: e.target.value })}
        >
          <option value="correct">Correct</option>
          <option value="incorrect">Incorrect</option>
        </select>
        <select onChange={e => setHostId(e.target.value)} value={hostId}>
          <option value="">Select</option>
          {hosts.map(h => (
           <option key={h.hostid} value={h.hostid}>{h.host}</option>
          ))}
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
        {status && <p style={{ marginTop: 10 }}>{status}</p>}
      </div>
    </div>
  );
}

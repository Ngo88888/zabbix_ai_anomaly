// App.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend, ResponsiveContainer } from "recharts";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const API_BASE = "http://localhost:8000"; // chỉnh nếu cần

export default function App() {
  const [hosts, setHosts] = useState([]);
  const [selectedHost, setSelectedHost] = useState("");
  const [category, setCategory] = useState("CPU");
  const [chartData, setChartData] = useState([]);
  const [aiResult, setAiResult] = useState(null);
  const [feedback, setFeedback] = useState({ feedback: "correct", comment: "" });

  // Fake host list (có thể fetch sau)
  useEffect(() => {
    // Giả lập host list nếu chưa có API
    setHosts([
      { hostid: "10101", name: "Web Server" },
      { hostid: "10102", name: "Database Server" }
    ]);
  }, []);

  const fetchChart = async () => {
    if (!selectedHost) return;
    const res = await axios.get(`${API_BASE}/chart_data`, {
      params: { host_id: selectedHost, category }
    });
    setChartData(res.data);
  };

  const callAI = async (type = "root_cause") => {
    if (!selectedHost) return;
    const res = await axios.post(`${API_BASE}/${type === "root_cause" ? "root_cause_analysis" : "detect_anomalies"}`, null, {
      params: { host_id: selectedHost }
    });
    setAiResult(res.data);
  };

  const submitFeedback = async () => {
    if (!selectedHost) return;
    await axios.post(`${API_BASE}/submit_feedback`, {
      host_id: selectedHost,
      ...feedback
    });
    alert("✅ Feedback submitted!");
    setFeedback({ feedback: "correct", comment: "" });
  };

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold">Zabbix + AI Monitoring Dashboard</h1>

      {/* Host + Category Selector */}
      <div className="flex gap-4">
        <select
          className="border p-2 rounded"
          value={selectedHost}
          onChange={(e) => setSelectedHost(e.target.value)}
        >
          <option value="">-- Select Host --</option>
          {hosts.map((h) => (
            <option key={h.hostid} value={h.hostid}>{h.name}</option>
          ))}
        </select>

        <select
          className="border p-2 rounded"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          {['CPU', 'Memory', 'Disk', 'Network', 'Service'].map((cat) => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>

        <Button onClick={fetchChart}>📊 Load Chart</Button>
      </div>

      {/* Chart */}
      {chartData.length > 0 && (
        <Card>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="value" stroke="#8884d8" name="Metric Value" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* AI Insight */}
      <div className="flex gap-4">
        <Button onClick={() => callAI("root_cause")}>🤖 Root Cause</Button>
        <Button onClick={() => callAI("anomaly")}>📉 Anomalies</Button>
      </div>

      {aiResult && (
        <Card>
          <CardContent>
            <pre className="whitespace-pre-wrap text-sm">
              {JSON.stringify(aiResult, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}

      {/* Feedback Form */}
      <div className="space-y-2">
        <h2 className="text-xl font-semibold">Gửi Feedback</h2>
        <div className="flex gap-4">
          <select
            className="border p-2 rounded"
            value={feedback.feedback}
            onChange={(e) => setFeedback({ ...feedback, feedback: e.target.value })}
          >
            <option value="correct">✅ Đúng</option>
            <option value="incorrect">❌ Sai</option>
          </select>
          <input
            className="border p-2 rounded flex-1"
            placeholder="Ghi chú thêm..."
            value={feedback.comment}
            onChange={(e) => setFeedback({ ...feedback, comment: e.target.value })}
          />
          <Button onClick={submitFeedback}>📨 Gửi</Button>
        </div>
      </div>
    </div>
  );
}

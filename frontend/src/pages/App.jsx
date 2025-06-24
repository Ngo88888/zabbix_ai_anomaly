import React, { useEffect, useState } from 'react';
import { 
  getHosts, 
  getChartData, 
  detectAnomalies, 
  submitFeedback 
} from '../services/api';
import HostSelector from '../components/HostSelector';
import CategorySelector from '../components/CategorySelector';
import MetricsChart from '../components/MetricsChart';
import AnomalyDisplay from '../components/AnomalyDisplay';
import FeedbackForm from '../components/FeedbackForm';
import '../styles/App.css';

/**
 * Main application component
 */
const App = () => {
  const [hosts, setHosts] = useState([]);
  const [hostId, setHostId] = useState('');
  const [category, setCategory] = useState('CPU');
  const [chartData, setChartData] = useState([]);
  const [anomalyData, setAnomalyData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Load hosts on component mount
  useEffect(() => {
    const loadHosts = async () => {
      try {
        const data = await getHosts();
        setHosts(data);
      } catch (err) {
        console.error('Failed to load hosts:', err);
        setError('Failed to load hosts. Please try again later.');
      }
    };

    loadHosts();
  }, []);

  // Handle host change
  const handleHostChange = (newHostId) => {
    setHostId(newHostId);
    setChartData([]);
    setAnomalyData(null);
  };

  // Handle category change
  const handleCategoryChange = (newCategory) => {
    setCategory(newCategory);
    if (hostId) {
      loadChartData(hostId, newCategory);
    }
  };

  // Load chart data
  const loadChartData = async (id, cat) => {
    if (!id) return;
    
    setLoading(true);
    setError('');
    
    try {
      const data = await getChartData(id, cat);
      setChartData(data);
    } catch (err) {
      console.error('Failed to load chart data:', err);
      setError('Failed to load chart data. Please try again later.');
      setChartData([]);
    } finally {
      setLoading(false);
    }
  };

  // Handle chart load button click
  const handleLoadChart = () => {
    loadChartData(hostId, category);
  };

  // Handle anomaly detection button click
  const handleDetectAnomalies = async () => {
    if (!hostId) return;
    
    setLoading(true);
    setError('');
    
    try {
      const data = await detectAnomalies(hostId);
      setAnomalyData(data);
    } catch (err) {
      console.error('Failed to detect anomalies:', err);
      setError('Failed to detect anomalies. Please try again later.');
      setAnomalyData(null);
    } finally {
      setLoading(false);
    }
  };

  // Handle feedback submission
  const handleFeedbackSubmit = async (hostId, feedback, comment) => {
    return await submitFeedback(hostId, feedback, comment);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Zabbix AI Anomaly Detection</h1>
      </header>

      <main className="app-content">
        <section className="controls-section">
          <div className="selectors">
            <HostSelector 
              hosts={hosts} 
              hostId={hostId} 
              onHostChange={handleHostChange} 
            />
            <CategorySelector 
              category={category} 
              onCategoryChange={handleCategoryChange} 
            />
          </div>
          
          <div className="action-buttons">
            <button onClick={handleLoadChart} disabled={!hostId || loading}>
              Load Chart
            </button>
            <button onClick={handleDetectAnomalies} disabled={!hostId || loading}>
              Detect Anomalies
            </button>
          </div>
        </section>

        {error && <div className="error-message">{error}</div>}
        {loading && <div className="loading-message">Loading...</div>}

        <section className="chart-section">
          <h2>Metrics Chart</h2>
          <MetricsChart data={chartData} />
        </section>

        {anomalyData && (
          <section className="anomaly-section">
            <AnomalyDisplay anomalyData={anomalyData} />
          </section>
        )}

        <section className="feedback-section">
          <FeedbackForm 
            hostId={hostId} 
            onSubmit={handleFeedbackSubmit} 
          />
        </section>
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} Zabbix AI Anomaly Detection</p>
      </footer>
    </div>
  );
};

export default App;

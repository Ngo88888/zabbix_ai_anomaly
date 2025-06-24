/**
 * API service for interacting with the backend
 */
import axios from 'axios';

// Get API URL from environment or use default
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Get all hosts
 * @returns {Promise<Array>} List of hosts
 */
export const getHosts = async () => {
  const response = await api.get('/get_hosts');
  return response.data;
};

/**
 * Get chart data for a host and category
 * @param {string} hostId - Host ID
 * @param {string} category - Category
 * @returns {Promise<Array>} Chart data
 */
export const getChartData = async (hostId, category) => {
  const response = await api.get('/chart_data', {
    params: { host_id: hostId, category },
  });
  return response.data;
};

/**
 * Detect anomalies for a host
 * @param {string} hostId - Host ID
 * @param {number} timePeriod - Time period in hours
 * @returns {Promise<Object>} Anomaly detection results
 */
export const detectAnomalies = async (hostId, timePeriod = 24) => {
  const response = await api.post('/detect_anomalies', null, {
    params: { host_id: hostId, time_period: timePeriod },
  });
  return response.data;
};

/**
 * Analyze root cause for a host
 * @param {string} hostId - Host ID
 * @param {number} timePeriod - Time period in hours
 * @returns {Promise<Object>} Root cause analysis results
 */
export const analyzeRootCause = async (hostId, timePeriod = 24) => {
  const response = await api.post('/root_cause_analysis', null, {
    params: { host_id: hostId, time_period: timePeriod },
  });
  return response.data;
};

/**
 * Submit feedback
 * @param {string} hostId - Host ID
 * @param {string} feedback - Feedback (correct/incorrect)
 * @param {string} comment - Comment
 * @returns {Promise<Object>} Submission result
 */
export const submitFeedback = async (hostId, feedback, comment) => {
  const response = await api.post('/submit_feedback', {
    host_id: hostId,
    feedback,
    comment,
  });
  return response.data;
}; 
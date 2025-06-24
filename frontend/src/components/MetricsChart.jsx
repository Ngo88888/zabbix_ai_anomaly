import React from 'react';
import PropTypes from 'prop-types';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';

/**
 * Metrics chart component
 */
const MetricsChart = ({ data }) => {
  if (!data || data.length === 0) {
    return <div className="no-data">No chart data available</div>;
  }

  return (
    <div className="metrics-chart">
      <LineChart width={800} height={300} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="value" stroke="#8884d8" />
      </LineChart>
    </div>
  );
};

MetricsChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      metric: PropTypes.string,
      time: PropTypes.string,
      value: PropTypes.number,
    })
  ),
};

MetricsChart.defaultProps = {
  data: [],
};

export default MetricsChart; 
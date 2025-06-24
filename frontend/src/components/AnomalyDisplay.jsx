import React from 'react';
import PropTypes from 'prop-types';

/**
 * Anomaly display component
 */
const AnomalyDisplay = ({ anomalyData }) => {
  if (!anomalyData || !anomalyData.anomalies || anomalyData.anomalies.length === 0) {
    return <div className="no-anomalies">No anomalies detected</div>;
  }

  return (
    <div className="anomaly-display">
      <h3>Detected Anomalies:</h3>
      {anomalyData.anomalies.map((anomaly, index) => (
        <div key={index} className="anomaly-card">
          <h4>Metric: {anomaly.metric}</h4>
          <p><strong>Severity:</strong> {anomaly.severity}</p>
          <p><strong>Cause:</strong> {anomaly.cause}</p>
          <p><strong>Recommended Action:</strong> {anomaly.action}</p>
        </div>
      ))}
    </div>
  );
};

AnomalyDisplay.propTypes = {
  anomalyData: PropTypes.shape({
    anomalies: PropTypes.arrayOf(
      PropTypes.shape({
        metric: PropTypes.string,
        severity: PropTypes.string,
        cause: PropTypes.string,
        action: PropTypes.string,
      })
    ),
  }),
};

AnomalyDisplay.defaultProps = {
  anomalyData: { anomalies: [] },
};

export default AnomalyDisplay; 
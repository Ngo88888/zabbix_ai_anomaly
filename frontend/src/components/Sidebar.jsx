import React, { useState } from 'react';
import PropTypes from 'prop-types';

/**
 * Sidebar component for the left side of the UI
 */
const Sidebar = ({ hostId, onAnalyzeRootCause, activeTab, onTabChange }) => {
  const [isOpen, setIsOpen] = useState(true);
  const [loading, setLoading] = useState(false);
  const [rootCauseData, setRootCauseData] = useState(null);

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  const handleAnalyzeClick = async () => {
    if (!hostId) return;
    
    setLoading(true);
    try {
      const data = await onAnalyzeRootCause(hostId);
      setRootCauseData(data);
    } catch (error) {
      console.error('Error analyzing root cause:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <div className="sidebar-toggle" onClick={toggleSidebar}>
        {isOpen ? '‹' : '›'}
      </div>
      
      <div className="sidebar-content">
        <div className="sidebar-logo">
          <h2>Zabbix AI</h2>
        </div>
        
        <div className="sidebar-tabs">
          <button 
            className={`sidebar-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => onTabChange('dashboard')}
          >
            <i className="tab-icon">📊</i>
            <span className="tab-text">Zabbix Dashboard</span>
          </button>
          
          <button 
            className={`sidebar-tab ${activeTab === 'analysis' ? 'active' : ''}`}
            onClick={() => onTabChange('analysis')}
          >
            <i className="tab-icon">🔍</i>
            <span className="tab-text">AI Analysis</span>
          </button>
        </div>
        
        {activeTab === 'analysis' && (
          <div className="sidebar-section">
            <h4>Root Cause Analysis</h4>
            <button 
              onClick={handleAnalyzeClick} 
              disabled={!hostId || loading}
              className="sidebar-button"
            >
              {loading ? 'Analyzing...' : 'Analyze Root Cause'}
            </button>
            
            {rootCauseData && (
              <div className="root-cause-results">
                <h5>Analysis Results:</h5>
                <div className="result-item">
                  <strong>Root Cause:</strong> 
                  <p>{rootCauseData.root_cause}</p>
                </div>
                
                <div className="result-item">
                  <strong>Confidence:</strong> 
                  <p>{rootCauseData.confidence}</p>
                </div>
                
                <div className="result-item">
                  <strong>Evidence:</strong>
                  <ul>
                    {rootCauseData.evidence.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="result-item">
                  <strong>Recommendation:</strong>
                  <p>{rootCauseData.recommendation}</p>
                </div>
              </div>
            )}
          </div>
        )}
        
        <div className="sidebar-section">
          <h4>Quick Links</h4>
          <ul className="sidebar-links">
            <li><a href="#">Documentation</a></li>
            <li><a href="#">System Status</a></li>
            <li><a href="#">Settings</a></li>
          </ul>
        </div>
        
        <div className="sidebar-footer">
          <div className="system-info">
            <p><strong>Version:</strong> 1.0.0</p>
            <p><strong>Status:</strong> <span className="status-active">Active</span></p>
          </div>
        </div>
      </div>
    </div>
  );
};

Sidebar.propTypes = {
  hostId: PropTypes.string,
  onAnalyzeRootCause: PropTypes.func.isRequired,
  activeTab: PropTypes.string.isRequired,
  onTabChange: PropTypes.func.isRequired
};

Sidebar.defaultProps = {
  hostId: '',
};

export default Sidebar; 
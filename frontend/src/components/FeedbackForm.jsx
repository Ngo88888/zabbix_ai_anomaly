import React, { useState } from 'react';
import PropTypes from 'prop-types';

/**
 * Feedback form component
 */
const FeedbackForm = ({ hostId, onSubmit }) => {
  const [feedback, setFeedback] = useState('correct');
  const [comment, setComment] = useState('');
  const [status, setStatus] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await onSubmit(hostId, feedback, comment);
      setStatus('✅ Feedback submitted!');
      setComment('');
    } catch (error) {
      setStatus('❌ Error submitting feedback');
      console.error(error);
    }
  };

  return (
    <div className="feedback-form">
      <h3>Feedback</h3>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Assessment:</label>
          <select
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
          >
            <option value="correct">Correct</option>
            <option value="incorrect">Incorrect</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>Comment:</label>
          <textarea
            rows="3"
            cols="50"
            placeholder="Comment..."
            value={comment}
            onChange={(e) => setComment(e.target.value)}
          />
        </div>
        
        <button type="submit" disabled={!hostId}>Submit Feedback</button>
        {status && <p className="status-message">{status}</p>}
      </form>
    </div>
  );
};

FeedbackForm.propTypes = {
  hostId: PropTypes.string,
  onSubmit: PropTypes.func.isRequired,
};

FeedbackForm.defaultProps = {
  hostId: '',
};

export default FeedbackForm; 
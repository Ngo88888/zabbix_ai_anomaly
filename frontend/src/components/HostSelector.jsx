import React from 'react';
import PropTypes from 'prop-types';

/**
 * Host selector component
 */
const HostSelector = ({ hosts, hostId, onHostChange }) => {
  return (
    <div className="host-selector">
      <label>Host: </label>
      <select 
        onChange={(e) => onHostChange(e.target.value)} 
        value={hostId}
      >
        <option value="">Select a host</option>
        {hosts.map((host) => (
          <option key={host.hostid} value={host.hostid}>
            {host.host}
          </option>
        ))}
      </select>
    </div>
  );
};

HostSelector.propTypes = {
  hosts: PropTypes.arrayOf(
    PropTypes.shape({
      hostid: PropTypes.string.isRequired,
      host: PropTypes.string.isRequired,
    })
  ).isRequired,
  hostId: PropTypes.string,
  onHostChange: PropTypes.func.isRequired,
};

HostSelector.defaultProps = {
  hostId: '',
};

export default HostSelector; 
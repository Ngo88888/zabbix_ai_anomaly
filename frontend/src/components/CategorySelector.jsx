import React from 'react';
import PropTypes from 'prop-types';

/**
 * Category selector component
 */
const CategorySelector = ({ category, onCategoryChange }) => {
  const categories = ['CPU', 'Memory', 'Disk', 'Network', 'Service', 'Other'];

  return (
    <div className="category-selector">
      <label>Category: </label>
      <select
        onChange={(e) => onCategoryChange(e.target.value)}
        value={category}
      >
        {categories.map((cat) => (
          <option key={cat} value={cat}>
            {cat}
          </option>
        ))}
      </select>
    </div>
  );
};

CategorySelector.propTypes = {
  category: PropTypes.string.isRequired,
  onCategoryChange: PropTypes.func.isRequired,
};

export default CategorySelector; 
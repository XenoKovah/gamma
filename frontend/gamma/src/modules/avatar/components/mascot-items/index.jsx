import React from 'react';
import clsx from 'clsx';
import PropTypes from 'prop-types';

import { useMascotStore } from '../../state/mascot.state';
import DrawMascotItem from '../draw-mascot-item';

const MascotItems = ({ items, selectedItem, dataKey }) => {
  const { setSelectedMascotData, isLoading } = useMascotStore();

  return (
    <ul className="mascot-wardrobe-list">
      {items.length > 0
        && items.map((item) => (
          <li key={`${dataKey}Item_${item.id}`}>
            <button
              className={clsx('mascot-wardrobe-list-item', {
                'is-active': selectedItem?.id === item.id,
                'is-disabled': selectedItem?.id === -1 || isLoading,
              })}
              type="button"
              onClick={() => {
                if (isLoading) {
                  return;
                }
                setSelectedMascotData({ [dataKey]: item });
              }}
              disabled={isLoading}
            >
              <div className="mascot-wardrobe-list-image-holder">
                <div className="mascot-wardrobe-list-image">
                  <DrawMascotItem item={item} dataKey={dataKey} />
                </div>
              </div>
              {item.name}
            </button>
          </li>
        ))}
    </ul>
  );
};

MascotItems.propTypes = {
  items: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      name: PropTypes.string.isRequired,
      svg_file: PropTypes.string, // Optional SVG file path
    }),
  ).isRequired, // `items` must be an array and is required
  selectedItem: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  }), // Optional selected item
  dataKey: PropTypes.string.isRequired, // Required string for dataKey
};

export default MascotItems;

import React, {
  createContext, useState, useContext, useMemo,
} from 'react';
import PropTypes from 'prop-types';

const BadgesContext = createContext();

/**
 * Provides context for the Badges module.
 * This provider is dynamically imported via Webpack's \`require.context()\`
 * from `modules/context/`, ensuring automatic discovery and initialization.
 */
const BadgesProvider = ({ children }) => {
  const [badgesContextData, setBadgesContextData] = useState([]);

  const contextValue = useMemo(() => ({
    badgesContextData, setBadgesContextData,
  }), [badgesContextData, setBadgesContextData]);

  return (
    <BadgesContext.Provider value={contextValue}>
      {children}
    </BadgesContext.Provider>
  );
};

BadgesProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export default BadgesProvider;

export const useBadgesContextData = () => useContext(BadgesContext);

import React, {
  createContext, useState, useContext, useMemo,
} from 'react';
import PropTypes from 'prop-types';

const AvatarsContext = createContext();

/**
 * Provides context for the Avatars module.
 * This provider is dynamically imported via Webpack's \`require.context()\`
 * from `modules/context/`, ensuring automatic discovery and initialization.
 */
const AvatarsProvider = ({ children }) => {
  const [avatarsContextData, setAvatarsContextData] = useState([]);

  const contextValue = useMemo(() => ({
    avatarsContextData, setAvatarsContextData,
  }), [avatarsContextData, setAvatarsContextData]);

  return (
    <AvatarsContext.Provider value={contextValue}>
      {children}
    </AvatarsContext.Provider>
  );
};

AvatarsProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export default AvatarsProvider;

export const useAvatarsContextData = () => useContext(AvatarsContext);

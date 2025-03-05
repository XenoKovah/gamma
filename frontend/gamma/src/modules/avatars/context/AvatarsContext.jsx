import React, {
  createContext, useState, useContext, useMemo,
} from 'react';
import PropTypes from 'prop-types';

const AvatarsContext = createContext();

/**
 * Provides context for the Avatars module.
 * This provider is dynamically imported via Webpack's `require.context()`
 * from `modules/context/`, ensuring automatic discovery and initialization.
 */
const AvatarsProvider = ({ children }) => {
  const [currentAvatarSetData, setCurrentAvatarSetData] = useState(null);

  const contextValue = useMemo(() => ({
    currentAvatarSetData,
    setCurrentAvatarSetData,
  }), [currentAvatarSetData, setCurrentAvatarSetData]);

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

export const useAvatarsContext = () => useContext(AvatarsContext);

import React, {
  createContext, useState, useContext, useMemo,
} from 'react';
import PropTypes from 'prop-types';

const AvatarContext = createContext();

/**
 * Provides context for the Avatar module.
 * This provider is dynamically imported via Webpack's \`require.context()\`
 * from `modules/context/`, ensuring automatic discovery and initialization.
 */
const AvatarProvider = ({ children }) => {
  const [avatarContextData, setAvatarContextData] = useState([]);

  const contextValue = useMemo(() => ({
    avatarContextData, setAvatarContextData,
  }), [avatarContextData, setAvatarContextData]);

  return (
    <AvatarContext.Provider value={contextValue}>
      {children}
    </AvatarContext.Provider>
  );
};

AvatarProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export default AvatarProvider;

export const useAvatarContextData = () => useContext(AvatarContext);

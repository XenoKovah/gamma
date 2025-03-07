import React from 'react';
import PropTypes from 'prop-types';
import {
  Button, Stack, useMediaQuery, breakpoints,
} from '@openedx/paragon';

const SubHeader = ({
  title, btnTitle, description, isError, onClick,
}) => {
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });

  return (
    <header className="my-4">
      <Stack className="justify-content-between" direction={isExtraSmall ? 'vertical' : 'horizontal'}>
        <h1 className="mb-0">{title}</h1>
        {!isError && (
          <Stack direction={isExtraSmall ? 'vertical' : 'horizontal'} gap={3}>
            <p className="m-0">
              {description}
            </p>
            <Button onClick={onClick}>
              {btnTitle}
            </Button>
          </Stack>
        )}
      </Stack>
    </header>
  );
};

SubHeader.propTypes = {
  title: PropTypes.string.isRequired,
  isError: PropTypes.bool.isRequired,
  btnTitle: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
};

export default SubHeader;

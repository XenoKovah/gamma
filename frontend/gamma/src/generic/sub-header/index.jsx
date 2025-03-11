import React from 'react';
import PropTypes from 'prop-types';
import {
  Button, Stack, useMediaQuery, breakpoints,
} from '@openedx/paragon';

const SubHeader = ({
  title, btnTitle, description, isError,
  onClick, headingLevel: Heading = 'h1', isDisabledActionBtn,
}) => {
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });

  return (
    <header className="my-4">
      <Stack className="justify-content-between" direction={isExtraSmall ? 'vertical' : 'horizontal'}>
        <Heading className="mb-0">{title}</Heading>
        {!isError && (
          <Stack direction={isExtraSmall ? 'vertical' : 'horizontal'} gap={3}>
            <p className="m-0">
              {description}
            </p>
            {btnTitle && (
              <Button onClick={onClick} disabled={isDisabledActionBtn}>
                {btnTitle}
              </Button>
            )}
          </Stack>
        )}
      </Stack>
    </header>
  );
};

SubHeader.propTypes = {
  title: PropTypes.string.isRequired,
  isError: PropTypes.bool.isRequired,
  btnTitle: PropTypes.string,
  description: PropTypes.string.isRequired,
  onClick: PropTypes.func,
  headingLevel: PropTypes.oneOf(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']),
  isDisabledActionBtn: PropTypes.bool,
};

SubHeader.defaultProps = {
  headingLevel: 'h1',
  isDisabledActionBtn: false,
  btnTitle: undefined,
  onClick: () => {},
};

export default SubHeader;

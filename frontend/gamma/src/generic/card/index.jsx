import React from 'react';
import PropTypes from 'prop-types';
import { Card as BaseCard, ActionRow, Button } from '@openedx/paragon';

const Card = ({
  id,
  title,
  src,
  prevBtnTitle,
  nextBtnTitle,
  onPrevBtnClick,
  onNextBtnClick,
}) => (
  <BaseCard className="card-item" data-testid={`card-item-${id}`}>
    <BaseCard.ImageCap
      className="card-item-image"
      src={src}
      srcAlt={title}
    />
    <BaseCard.Header className="card-item-header" title={title} />
    <BaseCard.Footer>
      <ActionRow>
        <Button variant="tertiary" block onClick={onPrevBtnClick}>
          {prevBtnTitle}
        </Button>
        <Button className="mt-0" block onClick={onNextBtnClick}>
          {nextBtnTitle}
        </Button>
      </ActionRow>
    </BaseCard.Footer>
  </BaseCard>
);

Card.propTypes = {
  id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  title: PropTypes.string.isRequired,
  src: PropTypes.string.isRequired,
  prevBtnTitle: PropTypes.string.isRequired,
  nextBtnTitle: PropTypes.string.isRequired,
  onPrevBtnClick: PropTypes.func,
  onNextBtnClick: PropTypes.func,
};

Card.defaultProps = {
  onPrevBtnClick: () => {},
  onNextBtnClick: () => {},
};

export default Card;

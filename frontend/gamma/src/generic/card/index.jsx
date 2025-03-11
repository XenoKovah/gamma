import React from 'react';
import PropTypes from 'prop-types';
import {
  Card as BaseCard, ActionRow, Button, Badge,
} from '@openedx/paragon';

const Card = ({
  id,
  src,
  title,
  section,
  subtitle,
  badgeText,
  prevBtnTitle,
  nextBtnTitle,
  onPrevBtnClick,
  onNextBtnClick,
}) => (
  <BaseCard className="card-item" data-testid={`card-item-${id}`}>
    {badgeText && (
      <Badge
        variant="warning"
        className="card-item-badge"
      >
        {badgeText}
      </Badge>
    )}
    <BaseCard.ImageCap
      className="card-item-image"
      src={src}
      srcAlt={title}
    />
    <BaseCard.Header
      className="card-item-header"
      title={title}
      subtitle={subtitle}
    />
    {section && (
      <BaseCard.Section title={section.title}>
        {section.content}
      </BaseCard.Section>
    )}
    <BaseCard.Footer>
      <ActionRow>
        {prevBtnTitle && (
          <Button variant="tertiary" block onClick={onPrevBtnClick}>
            {prevBtnTitle}
          </Button>
        )}
        {nextBtnTitle && (
          <Button className="mt-0" block onClick={onNextBtnClick}>
            {nextBtnTitle}
          </Button>
        )}
      </ActionRow>
    </BaseCard.Footer>
  </BaseCard>
);

Card.propTypes = {
  id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  title: PropTypes.string.isRequired,
  subtitle: PropTypes.string,
  src: PropTypes.string.isRequired,
  section: PropTypes.shape({
    title: PropTypes.string,
    content: PropTypes.oneOfType([
      PropTypes.node,
      PropTypes.string,
      PropTypes.number,
    ]),
  }),
  prevBtnTitle: PropTypes.string,
  nextBtnTitle: PropTypes.string,
  onPrevBtnClick: PropTypes.func,
  onNextBtnClick: PropTypes.func,
  badgeText: PropTypes.string,
};

Card.defaultProps = {
  subtitle: undefined,
  section: null,
  prevBtnTitle: undefined,
  nextBtnTitle: undefined,
  badgeText: undefined,
  onPrevBtnClick: () => {},
  onNextBtnClick: () => {},
};

export default Card;

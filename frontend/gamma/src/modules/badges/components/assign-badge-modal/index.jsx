import React, { useEffect, useMemo, useState } from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { Form } from '@openedx/paragon';

import { Modal } from '../../../../generic';
import messages from '../../i18n';

/**
 * Parse a free-text blob of user IDs into a de-duplicated, order-preserving list.
 * Accepts IDs separated by commas, semicolons, whitespace, or newlines.
 */
export const parseUserIds = (text) => {
  const ids = text
    .split(/[\s,;]+/)
    .map((value) => value.trim())
    .filter(Boolean);
  return [...new Set(ids)];
};

const AssignBadgeModal = ({
  isOpen, badge, onClose, onAssign, isAssigning,
}) => {
  const intl = useIntl();
  const [userIdsText, setUserIdsText] = useState('');

  // Clear the textarea whenever the modal is closed so it reopens empty.
  useEffect(() => {
    if (!isOpen) {
      setUserIdsText('');
    }
  }, [isOpen]);

  const userIds = useMemo(() => parseUserIds(userIdsText), [userIdsText]);

  const handleSubmit = () => {
    if (badge && userIds.length) {
      onAssign(badge.id, userIds);
    }
  };

  return (
    <Modal
      title={intl.formatMessage(messages.assignBadgeModalTitle, { title: badge?.title || '' })}
      isOpen={isOpen}
      handleClose={onClose}
      hasCloseButton
      size="lg"
      isOverflowVisible={false}
      submitBtnOptions={{
        title: intl.formatMessage(messages.assignBadgeModalSubmitBtnText),
        submitFn: handleSubmit,
        disabled: userIds.length === 0 || isAssigning,
      }}
    >
      <p>{intl.formatMessage(messages.assignBadgeModalDescription)}</p>
      {badge?.points > 0 && (
        <p className="font-weight-bold">
          {intl.formatMessage(messages.assignBadgeModalPointsNote, { points: badge.points })}
        </p>
      )}
      <Form.Group controlId="assignBadgeUserIds">
        <Form.Label>{intl.formatMessage(messages.assignBadgeModalUserIdsLabel)}</Form.Label>
        <Form.Control
          as="textarea"
          rows={6}
          name="userIds"
          data-testid="assign-badge-user-ids"
          value={userIdsText}
          onChange={(event) => setUserIdsText(event.target.value)}
          placeholder={intl.formatMessage(messages.assignBadgeModalUserIdsPlaceholder)}
        />
      </Form.Group>
      {userIds.length > 0 && (
        <p className="small text-muted mb-0">
          {intl.formatMessage(messages.assignBadgeModalSelectedCount, { count: userIds.length })}
        </p>
      )}
    </Modal>
  );
};

AssignBadgeModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onAssign: PropTypes.func.isRequired,
  isAssigning: PropTypes.bool,
  badge: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    title: PropTypes.string,
    points: PropTypes.number,
  }),
};

AssignBadgeModal.defaultProps = {
  isAssigning: false,
  badge: null,
};

export default AssignBadgeModal;

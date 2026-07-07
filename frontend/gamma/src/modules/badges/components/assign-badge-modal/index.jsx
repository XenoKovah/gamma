import React, { useEffect, useMemo, useState } from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { Form, Alert } from '@openedx/paragon';

import { Modal } from '../../../../generic';
import { resolveIdentifiersToUsernames } from '../../data';
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

const MODE_MESSAGES = {
  assign: {
    title: messages.assignBadgeModalTitle,
    description: messages.assignBadgeModalDescription,
    pointsNote: messages.assignBadgeModalPointsNote,
    submit: messages.assignBadgeModalSubmitBtnText,
    selectedCount: messages.assignBadgeModalSelectedCount,
  },
  unassign: {
    title: messages.unassignBadgeModalTitle,
    description: messages.unassignBadgeModalDescription,
    pointsNote: messages.unassignBadgeModalPointsNote,
    submit: messages.unassignBadgeModalSubmitBtnText,
    selectedCount: messages.unassignBadgeModalSelectedCount,
  },
};

const AssignBadgeModal = ({
  isOpen, badge, mode, onClose, onSubmit, isSubmitting,
}) => {
  const intl = useIntl();
  const [userIdsText, setUserIdsText] = useState('');
  const [isResolving, setIsResolving] = useState(false);
  const [unresolvedEmails, setUnresolvedEmails] = useState([]);
  const modeMessages = MODE_MESSAGES[mode] || MODE_MESSAGES.assign;

  // Clear the textarea (and any previous lookup error) whenever the modal closes
  // so it reopens empty.
  useEffect(() => {
    if (!isOpen) {
      setUserIdsText('');
      setUnresolvedEmails([]);
    }
  }, [isOpen]);

  const userIds = useMemo(() => parseUserIds(userIdsText), [userIdsText]);

  // Entries may be usernames or emails. Emails are resolved to usernames against
  // the LMS (the gamma service has no email); if any can't be matched we surface
  // them and do NOT submit, rather than assigning to a bogus user.
  const handleSubmit = async () => {
    if (!badge || !userIds.length) {
      return;
    }
    setUnresolvedEmails([]);
    setIsResolving(true);
    try {
      const { usernames, unresolved } = await resolveIdentifiersToUsernames(userIds);
      if (unresolved.length) {
        setUnresolvedEmails(unresolved);
        return;
      }
      onSubmit(badge.id, usernames);
    } finally {
      setIsResolving(false);
    }
  };

  return (
    <Modal
      title={intl.formatMessage(modeMessages.title, { title: badge?.title || '' })}
      isOpen={isOpen}
      handleClose={onClose}
      hasCloseButton
      size="lg"
      isOverflowVisible={false}
      submitBtnOptions={{
        title: intl.formatMessage(modeMessages.submit),
        submitFn: handleSubmit,
        disabled: userIds.length === 0 || isSubmitting || isResolving,
      }}
    >
      <p>{intl.formatMessage(modeMessages.description)}</p>
      {badge?.points > 0 && (
        <p className="font-weight-bold">
          {intl.formatMessage(modeMessages.pointsNote, { points: badge.points })}
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
          onChange={(event) => {
            setUserIdsText(event.target.value);
            setUnresolvedEmails([]);
          }}
          placeholder={intl.formatMessage(messages.assignBadgeModalUserIdsPlaceholder)}
        />
      </Form.Group>
      {unresolvedEmails.length > 0 && (
        <Alert variant="danger" className="mb-2" data-testid="assign-badge-unresolved-emails">
          {intl.formatMessage(messages.assignBadgeModalUnresolvedEmailsError, {
            emails: unresolvedEmails.join(', '),
          })}
        </Alert>
      )}
      {userIds.length > 0 && (
        <p className="small text-muted mb-0">
          {intl.formatMessage(modeMessages.selectedCount, { count: userIds.length })}
        </p>
      )}
    </Modal>
  );
};

AssignBadgeModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  mode: PropTypes.oneOf(['assign', 'unassign']),
  isSubmitting: PropTypes.bool,
  badge: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    title: PropTypes.string,
    points: PropTypes.number,
  }),
};

AssignBadgeModal.defaultProps = {
  mode: 'assign',
  isSubmitting: false,
  badge: null,
};

export default AssignBadgeModal;

import React, { useCallback, useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { Alert, Button, Form } from '@openedx/paragon';

import { Modal } from '../../../../generic';
import { fetchBadgeHolders, setBadgeExpiry, expireBadge } from '../../data';
import { endOfDayIso, formatExpiryDate } from '../../utils';
import messages from '../../i18n';

/**
 * Per-user expiry management for an expiring badge: lists the holders with when each grant
 * lapses, and lets an admin re-date the selected ones, make them permanent, or expire them now.
 * Points are never touched; an expired grant can be restored by giving it a later date.
 */
const ExpiryBadgeModal = ({ isOpen, badge, onClose }) => {
  const intl = useIntl();
  const [holders, setHolders] = useState([]);
  const [selected, setSelected] = useState([]);
  const [dateValue, setDateValue] = useState('');
  const [isBusy, setIsBusy] = useState(false);
  const [error, setError] = useState(false);
  const [notice, setNotice] = useState('');

  const badgeId = badge?.id;
  const neverLabel = intl.formatMessage(messages.expiryNever);

  const load = useCallback(async () => {
    if (!badgeId) {
      return;
    }
    setIsBusy(true);
    try {
      setHolders(await fetchBadgeHolders(badgeId));
      setError(false);
    } catch (e) {
      setError(true);
    } finally {
      setIsBusy(false);
    }
  }, [badgeId]);

  useEffect(() => {
    if (isOpen) {
      load();
    } else {
      setHolders([]);
      setSelected([]);
      setDateValue('');
      setNotice('');
      setError(false);
    }
  }, [isOpen, load]);

  const toggle = (userUid) => setSelected(
    (current) => (current.includes(userUid) ? current.filter((uid) => uid !== userUid) : [...current, userUid]),
  );
  const allSelected = holders.length > 0 && selected.length === holders.length;

  const run = async (action, doneMessage) => {
    setIsBusy(true);
    setNotice('');
    try {
      const result = await action();
      setNotice(intl.formatMessage(doneMessage, { count: result?.updated?.length || 0 }));
      setSelected([]);
      setHolders(await fetchBadgeHolders(badgeId));
      setError(false);
    } catch (e) {
      setError(true);
    } finally {
      setIsBusy(false);
    }
  };

  const handleSetDate = () => run(
    () => setBadgeExpiry(badgeId, selected, endOfDayIso(dateValue)),
    messages.expiryUpdatedNotice,
  );
  const handleMakePermanent = () => run(() => setBadgeExpiry(badgeId, selected, null), messages.expiryUpdatedNotice);
  const handleExpireNow = () => run(() => expireBadge(badgeId, selected), messages.expiryExpiredNotice);

  const noneSelected = selected.length === 0;

  return (
    <Modal
      title={intl.formatMessage(messages.expiryModalTitle, { title: badge?.title || '' })}
      isOpen={isOpen}
      handleClose={onClose}
      hasCloseButton
      size="lg"
      isOverflowVisible={false}
      isFullscreenScroll
      closeBtnTitle={intl.formatMessage(messages.expiryModalCloseBtnText)}
      submitBtnOptions={{
        title: intl.formatMessage(messages.expirySetDateBtnText),
        submitFn: handleSetDate,
        disabled: noneSelected || !dateValue || isBusy,
      }}
    >
      <p>{intl.formatMessage(messages.expiryModalDescription)}</p>
      {error && (
        <Alert variant="danger" data-testid="expiry-error">{intl.formatMessage(messages.expiryError)}</Alert>
      )}
      {notice && <Alert variant="success" data-testid="expiry-notice">{notice}</Alert>}
      {holders.length === 0 && !isBusy && !error && (
        <p className="text-muted" data-testid="expiry-no-holders">{intl.formatMessage(messages.expiryNoHolders)}</p>
      )}
      {holders.length > 0 && (
        <table className="table table-sm" data-testid="expiry-holders">
          <thead>
            <tr>
              <th>
                <Form.Checkbox
                  checked={allSelected}
                  onChange={() => setSelected(allSelected ? [] : holders.map((holder) => holder.userUid))}
                  aria-label={intl.formatMessage(messages.expirySelectAll)}
                />
              </th>
              <th>{intl.formatMessage(messages.expiryUserColumn)}</th>
              <th>{intl.formatMessage(messages.expiryExpiresColumn)}</th>
            </tr>
          </thead>
          <tbody>
            {holders.map((holder) => (
              <tr key={holder.userUid}>
                <td>
                  <Form.Checkbox
                    checked={selected.includes(holder.userUid)}
                    onChange={() => toggle(holder.userUid)}
                    aria-label={holder.userUid}
                  />
                </td>
                <td>{holder.userUid}</td>
                <td className={holder.isExpired ? 'text-danger' : ''}>
                  {formatExpiryDate(holder.expiresAt, neverLabel)}
                  {holder.isExpired && ` (${intl.formatMessage(messages.expiryExpiredTag)})`}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <Form.Group controlId="expiryNewDate">
        <Form.Label>{intl.formatMessage(messages.expiryDateLabel)}</Form.Label>
        <Form.Control
          type="date"
          name="expiryDate"
          data-testid="expiry-date"
          value={dateValue}
          onChange={(event) => setDateValue(event.target.value)}
        />
      </Form.Group>
      <div className="d-flex">
        <Button
          variant="outline-primary"
          className="mr-2"
          disabled={noneSelected || isBusy}
          onClick={handleMakePermanent}
        >
          {intl.formatMessage(messages.expiryMakePermanentBtnText)}
        </Button>
        <Button variant="outline-danger" disabled={noneSelected || isBusy} onClick={handleExpireNow}>
          {intl.formatMessage(messages.expiryExpireNowBtnText)}
        </Button>
      </div>
    </Modal>
  );
};

ExpiryBadgeModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  badge: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    title: PropTypes.string,
  }),
};

ExpiryBadgeModal.defaultProps = {
  badge: null,
};

export default ExpiryBadgeModal;

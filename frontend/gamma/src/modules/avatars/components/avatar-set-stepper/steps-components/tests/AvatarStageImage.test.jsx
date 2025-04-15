import React from 'react';
import { cleanup, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../../../../setupTests';
import moduleMessages from '../../../../i18n';
import { readFileAsDataURL } from '../../utils';
import AvatarStageImage from '../AvatarStageImage';

jest.mock('../../utils', () => ({
  readFileAsDataURL: jest.fn(),
}));

describe('AvatarStageImage', () => {
  const mockSetFieldValue = jest.fn();
  const mockOnRemove = jest.fn();

  const defaultProps = {
    index: 0,
    onRemove: mockOnRemove,
    setFieldValue: mockSetFieldValue,
    values: {
      avatars: [{ title: 'Avatar 1', description: 'Description 1', image: null }],
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(cleanup);

  const renderComponent = (props = {}) => renderWithProviders(<AvatarStageImage {...defaultProps} {...props} />);

  it('renders AvatarStageImage with correct title', () => {
    renderComponent();

    expect(
      screen.getByRole('heading', {
        name: moduleMessages.avatarSetStepperEvolutionAvatarStageTitle.defaultMessage.replace('{index}', 1),
      }),
    ).toBeInTheDocument();
  });

  it('renders a dropzone when no image is uploaded', () => {
    renderComponent();

    expect(screen.getByText('Drag and drop your file here or click to upload.')).toBeInTheDocument();
  });

  it('renders an image when an avatar is uploaded', () => {
    renderComponent({
      values: {
        avatars: [{ image: 'data:image/png;base64,somebase64string' }],
      },
    });

    expect(screen.getByRole('img')).toBeInTheDocument();
    expect(screen.getByRole('img')).toHaveAttribute('src', 'data:image/png;base64,somebase64string');
  });

  it('opens deletion confirmation modal when remove button is clicked', () => {
    const { getByRole, getByText } = renderComponent();

    const removeButton = getByRole('button', {
      name: moduleMessages.avatarSetStepperEvolutionRemoveAvatarBtn.defaultMessage,
    });
    userEvent.click(removeButton);

    expect(
      getByText(moduleMessages.confirmAvatarStageDeletionModalTitle.defaultMessage),
    ).toBeInTheDocument();
    expect(
      getByText(moduleMessages.confirmAvatarStageDeletionModalDescription.defaultMessage),
    ).toBeInTheDocument();
  });

  it('calls onRemove when delete is confirmed in the modal', () => {
    const { getByRole } = renderComponent();

    const removeButton = getByRole('button', {
      name: moduleMessages.avatarSetStepperEvolutionRemoveAvatarBtn.defaultMessage,
    });
    userEvent.click(removeButton);

    const deleteButton = getByRole('button', { name: /delete/i });
    userEvent.click(deleteButton);

    expect(mockOnRemove).toHaveBeenCalled();
  });

  it('closes the modal when cancel is clicked', () => {
    const { getByRole, getByText, queryByText } = renderComponent();

    const removeButton = getByRole('button', {
      name: moduleMessages.avatarSetStepperEvolutionRemoveAvatarBtn.defaultMessage,
    });
    userEvent.click(removeButton);

    expect(getByText(moduleMessages.confirmAvatarStageDeletionModalTitle.defaultMessage)).toBeInTheDocument();

    const cancelButton = getByRole('button', { name: /cancel/i });
    userEvent.click(cancelButton);

    expect(queryByText(moduleMessages.confirmAvatarStageDeletionModalTitle.defaultMessage)).not.toBeInTheDocument();
  });

  it('calls setFieldValue when a valid SVG file is uploaded', async () => {
    readFileAsDataURL.mockResolvedValue('data:image/svg+xml;base64,uploadedImage');

    renderComponent();

    const file = new File(['dummy content'], 'avatar.svg', { type: 'image/svg+xml' });
    const dropzone = screen.getByTestId('dropzone-container');
    const dropzoneInput = dropzone.querySelector('input[type="file"]');

    userEvent.upload(dropzoneInput, file);

    await waitFor(() => {
      expect(mockSetFieldValue).toHaveBeenCalledWith('avatars', [
        {
          title: moduleMessages.avatarSetStepperEvolutionAvatarDefaultTitle.defaultMessage.replace('{index}', 1),
          description: moduleMessages.avatarSetStepperEvolutionAvatarDefaultDescription.defaultMessage.replace('{index}', 1),
          image: 'data:image/svg+xml;base64,uploadedImage',
        },
      ]);
    });
  });

  it('handles file upload errors', async () => {
    readFileAsDataURL.mockRejectedValue(new Error('File read error'));

    renderComponent();

    const file = new File(['dummy content'], 'avatar.png', { type: 'image/png' });

    const dropzone = screen.getByTestId('dropzone-container');
    const dropzoneInput = dropzone.querySelector('input[type="file"]');

    userEvent.upload(dropzoneInput, file);

    await waitFor(() => {
      expect(mockSetFieldValue).not.toHaveBeenCalled();
    });
  });
});

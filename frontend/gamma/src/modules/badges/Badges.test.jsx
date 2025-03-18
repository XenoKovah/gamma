import React from 'react';
import axios from 'axios';
import '@testing-library/jest-dom';
import { cleanup, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../setupTests';
import genericMessages from '../../i18n';
import { submitBtnStatuses } from '../../generic/status-button';
import { useBadges } from './hooks/useBadges';
import { convertKeysToSnakeCase } from './data/utils';
import moduleMessages from './i18n';
import { fetchBadgesData, API_ROUTES } from './data';
import { Badges } from '.';

import { badgesMocks } from './__mocks__';

jest.mock('axios');
jest.mock('./data/hooks', () => ({
  useBadges: jest.fn(),
}));

jest.mock('./hooks/useBadges', () => ({
  useBadges: jest.fn(),
}));

const daysInTheWeek = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];

describe('Badges Component', () => {
  afterEach(cleanup);

  beforeEach(() => {
    window.HTMLElement.prototype.scrollIntoView = jest.fn();
    useBadges.mockReturnValue({
      isError: false,
      isLoading: false,
      badgesData: [],
      actionsData: [],
      coursesData: [],
      firstBadgeRef: null,
      submitStatus: submitBtnStatuses.DEFAULT,
      showErrorAlert: false,
      showErrorToast: false,
      deletionStatus: submitBtnStatuses.DEFAULT,
      setSubmitStatus: jest.fn(),
      setShowErrorToast: jest.fn(),
      setShowErrorAlert: jest.fn(),
      organizationsData: [],
      handleCreateNewBadge: jest.fn(),
      openManageEntityModal: jest.fn(),
      showBadgeCreatedAlert: false,
      handleDeleteBadgeById: jest.fn(),
      closeManageEntityModal: jest.fn(),
      isManageEntityModalOpen: false,
      openConfirmDeletionAlert: jest.fn(),
      closeDeletionManageEntityModal: jest.fn(),
      isDeletionManageEntityModalOpen: false,
    });
  });

  it('renders the footer on the page', async () => {
    useBadges.mockReturnValue({ badgesData: badgesMocks, isLoading: false, isError: false });

    const { getByRole } = renderWithProviders(<Badges />);

    const footer = getByRole('contentinfo');
    expect(footer).toBeInTheDocument();
  });

  it('displays the correct page heading', async () => {
    useBadges.mockReturnValue({ badgesData: badgesMocks, isLoading: false, isError: false });
    const { getByRole } = renderWithProviders(<Badges />);

    const heading = getByRole('heading', {
      level: 1, name: moduleMessages.pageTitle.defaultMessage,
    });
    expect(heading).toBeInTheDocument();
  });

  it('shows a loading spinner when the page is loading', async () => {
    useBadges.mockReturnValue({ badgesData: badgesMocks, isLoading: true, isError: false });
    const { getByRole } = renderWithProviders(<Badges />);

    const spinner = getByRole('status');
    expect(spinner).toBeInTheDocument();
  });

  it('displays an error message when the page fails to load badges', async () => {
    useBadges.mockReturnValue({ badgesData: badgesMocks, isLoading: false, isError: true });
    const { getByText, getByRole } = renderWithProviders(<Badges />);

    const errorHeading = getByText(genericMessages.alertDangerTitle.defaultMessage);
    expect(errorHeading).toBeInTheDocument();
    const errorMessage = getByText(genericMessages.alertDangerDescription.defaultMessage);
    expect(errorMessage).toBeInTheDocument();
    const dismissButton = getByRole('button', { name: 'Dismiss' });
    expect(dismissButton).toBeInTheDocument();
  });

  it('renders an empty badges list message when no badges are available', async () => {
    useBadges.mockReturnValue({ badgesData: [], isLoading: false, isError: false });
    const { getByText } = renderWithProviders(<Badges />);

    expect(getByText(moduleMessages.alertEmptyBadgesListTitle.defaultMessage)).toBeInTheDocument();
    expect(getByText(moduleMessages.alertEmptyBadgesListDescription.defaultMessage)).toBeInTheDocument();
  });

  it('shows the correct number of edit and delete buttons for each badge', async () => {
    useBadges.mockReturnValue({ badgesData: badgesMocks, isLoading: false, isError: false });

    const { getByText, getAllByRole } = renderWithProviders(<Badges />);

    badgesMocks.forEach((badge) => {
      expect(getByText(badge.title)).toBeInTheDocument();
      expect(getByText(badge.description)).toBeInTheDocument();
    });

    const editButtons = getAllByRole('button', {
      name: moduleMessages.badgeEditBtnTitle.defaultMessage,
    });
    const deleteButtons = getAllByRole('button', {
      name: moduleMessages.badgeDeleteBtnTitle.defaultMessage,
    });

    expect(editButtons).toHaveLength(badgesMocks.length);
    expect(deleteButtons).toHaveLength(badgesMocks.length);
  });

  it('correctly displays the total number of badges on the page', async () => {
    useBadges.mockReturnValue({ badgesData: badgesMocks, isLoading: false, isError: false });

    const { getByText } = renderWithProviders(<Badges />);

    expect(getByText(
      moduleMessages.totalBadgesCount.defaultMessage.replace('{badgesCount}', badgesMocks.length),
    )).toBeInTheDocument();
  });

  it('opens the modal and verifies its content when the add badge button is clicked', async () => {
    const setModalOpen = jest.fn();

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: false,
      openManageEntityModal: setModalOpen,
    }));

    const { rerender, getByTestId, getByRole } = renderWithProviders(<Badges />);

    const addNewBadgeBtn = getByTestId('add-badge-button');
    userEvent.click(addNewBadgeBtn);

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: true,
      openManageEntityModal: setModalOpen,
    }));

    rerender(<Badges />);

    await waitFor(() => {
      const modal = getByRole('dialog');
      expect(within(modal).getByText(moduleMessages.addManageEntityModalTitle.defaultMessage)).toBeInTheDocument();
      expect(within(modal).getByText(genericMessages.modalEntityInfoHeadingText.defaultMessage)).toBeInTheDocument();
      expect(within(modal).getByText(genericMessages.modalEntityImageHeadingText.defaultMessage)).toBeInTheDocument();
      expect(within(modal).getByRole('button', {
        name: genericMessages.modalEntityImageBtnUploadText.defaultMessage,
      })).toBeInTheDocument();
      expect(within(modal).getByText(genericMessages.modalEntityRulesTitle.defaultMessage)).toBeInTheDocument();

      const alertAboutEmptyRules = within(modal).getByRole('alert');
      expect(within(alertAboutEmptyRules)
        .getByText(genericMessages.modalEntityRulesAlertNoRulesTitle.defaultMessage)).toBeInTheDocument();
      expect(within(alertAboutEmptyRules)
        .getByText(genericMessages.modalEntityRulesAlertNoRulesDescription.defaultMessage)).toBeInTheDocument();
      expect(within(modal)
        .getByRole('button', { name: genericMessages.modalEntityRulesAddNewRuleBtnText.defaultMessage })).toBeInTheDocument();
      expect(within(modal)
        .getByRole('button', { name: genericMessages.modalDialogBtnStatefulDefaultText.defaultMessage })).toBeInTheDocument();
      expect(within(modal)
        .getByRole('button', { name: genericMessages.modalDialogBtnCancelText.defaultMessage })).toBeInTheDocument();

      const inputTitleElement = within(modal)
        .getByLabelText(genericMessages.modalEntityInfoLabelEntityTitle.defaultMessage);
      expect(inputTitleElement).toBeInTheDocument();
      const inputSlugElement = within(modal)
        .getByLabelText(genericMessages.modalEntityInfoLabelEntitySlugText.defaultMessage);
      expect(inputSlugElement).toBeInTheDocument();
      const inputActiveElement = within(modal)
        .getByLabelText(genericMessages.modalEntityInfoLabelEntityIsActiveText.defaultMessage);
      expect(inputActiveElement).toBeInTheDocument();
      const inputDescriptionElement = within(modal)
        .getByLabelText(genericMessages.modalEntityInfoLabelEntityDescriptionText.defaultMessage);
      expect(inputDescriptionElement).toBeInTheDocument();
    });
  });

  it('shows an error message when the title field is left empty', async () => {
    const setModalOpen = jest.fn();

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: false,
      openManageEntityModal: setModalOpen,
    }));

    const { rerender, getByTestId, getByRole } = renderWithProviders(<Badges />);

    const addNewBadgeBtn = getByTestId('add-badge-button');
    userEvent.click(addNewBadgeBtn);

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: true,
      openManageEntityModal: setModalOpen,
    }));

    rerender(<Badges />);

    await waitFor(() => {
      const modal = getByRole('dialog');
      const inputTitleElement = within(modal)
        .getByLabelText(genericMessages.modalEntityInfoLabelEntityTitle.defaultMessage);
      userEvent.click(inputTitleElement);
      userEvent.tab();
    });

    await waitFor(() => {
      const modal = getByRole('dialog');
      expect(
        within(modal).getByText(genericMessages.modalEntityValidationTitleRequiredText.defaultMessage),
      ).toBeInTheDocument();
    });
  });

  it('shows an error message when the slug field is left empty', async () => {
    const setModalOpen = jest.fn();

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: false,
      openManageEntityModal: setModalOpen,
    }));

    const { rerender, getByTestId, getByRole } = renderWithProviders(<Badges />);

    const addNewBadgeBtn = getByTestId('add-badge-button');
    userEvent.click(addNewBadgeBtn);

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: true,
      openManageEntityModal: setModalOpen,
    }));

    rerender(<Badges />);

    await waitFor(async () => {
      const modal = getByRole('dialog');
      const inputSlugElement = within(modal)
        .getByLabelText(genericMessages.modalEntityInfoLabelEntitySlugText.defaultMessage);
      userEvent.click(inputSlugElement);
      userEvent.tab();
    });

    await waitFor(() => {
      const modal = getByRole('dialog');
      expect(
        within(modal).getByText(genericMessages.modalEntityValidationSlugRequiredText.defaultMessage),
      ).toBeInTheDocument();
    });
  });

  it('shows an error message when the description field is left empty', async () => {
    const setModalOpen = jest.fn();

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: false,
      openManageEntityModal: setModalOpen,
    }));

    const { rerender, getByTestId, getByRole } = renderWithProviders(<Badges />);

    const addNewBadgeBtn = getByTestId('add-badge-button');
    userEvent.click(addNewBadgeBtn);

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: true,
      openManageEntityModal: setModalOpen,
    }));

    rerender(<Badges />);

    await waitFor(async () => {
      const modal = getByRole('dialog');
      const inputDescriptionElement = within(modal)
        .getByLabelText(genericMessages.modalEntityInfoLabelEntityDescriptionText.defaultMessage);
      expect(inputDescriptionElement).toBeInTheDocument();
      userEvent.click(inputDescriptionElement);
      userEvent.tab();
    });

    await waitFor(() => {
      const modal = getByRole('dialog');
      expect(
        within(modal).getByText(genericMessages.modalEntityValidationDescriptionRequiredText.defaultMessage),
      ).toBeInTheDocument();
    });
  });

  it('adds a new rule and verifies the modal content', async () => {
    const setModalOpen = jest.fn();

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: false,
      openManageEntityModal: setModalOpen,
    }));

    const { rerender, getByTestId, getByRole } = renderWithProviders(<Badges />);

    const addNewBadgeBtn = getByTestId('add-badge-button');
    userEvent.click(addNewBadgeBtn);

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: true,
      openManageEntityModal: setModalOpen,
    }));

    rerender(<Badges />);

    await waitFor(async () => {
      const modal = getByRole('dialog');
      const addNewRuleBtn = within(modal)
        .getByRole('button', { name: genericMessages.modalEntityRulesAddNewRuleBtnText.defaultMessage });
      userEvent.click(addNewRuleBtn);
    });

    await waitFor(async () => {
      const modal = getByRole('dialog');
      expect(within(modal)
        .getByText(genericMessages.modalEntityRulesActionHeadingTitle.defaultMessage)).toBeInTheDocument();
      expect(within(modal)
        .getByText(
          genericMessages.modalEntityActionEventNameLabelText.defaultMessage.replace('{eventType}', 'event type'),
        )).toBeInTheDocument();
      expect(within(modal)
        .getByLabelText(genericMessages.modalEntityRulesRuleEventTypeLabel.defaultMessage)).toBeInTheDocument();
      expect(within(modal)
        .getByLabelText(genericMessages.modalEntityRulesRuleCountLabel.defaultMessage)).toBeInTheDocument();
      expect(within(modal)
        .getByText(genericMessages.modalEntityRulesFiltersHeadingTitle.defaultMessage)).toBeInTheDocument();
      expect(within(modal)
        .getByText(genericMessages.modalEntityRulesFiltersSelectTitle.defaultMessage)).toBeInTheDocument();
      // Filters
      expect(within(modal)
        .getByText(genericMessages.modalEntityRulesRuleCourseLabel.defaultMessage)).toBeInTheDocument();
      expect(within(modal)
        .getByText(genericMessages.modalEntityOrganizationFilterTitle.defaultMessage)).toBeInTheDocument();
      expect(within(modal).getByText(/Frequency/i)).toBeInTheDocument();
      expect(within(modal).getByText(/Interval/i)).toBeInTheDocument();

      expect(within(modal)
        .getByRole('button', {
          name: genericMessages.modalEntityRulesBtnDeleteText.defaultMessage,
        })).toBeInTheDocument();
    });
  });

  it('validates required action fields when adding a new rule', async () => {
    const setModalOpen = jest.fn();

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: false,
      openManageEntityModal: setModalOpen,
    }));

    const { rerender, getByTestId, getByRole } = renderWithProviders(<Badges />);

    const addNewBadgeBtn = getByTestId('add-badge-button');
    userEvent.click(addNewBadgeBtn);

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: true,
      openManageEntityModal: setModalOpen,
    }));

    rerender(<Badges />);

    await waitFor(async () => {
      const modal = getByRole('dialog');
      const addNewRuleBtn = within(modal)
        .getByRole('button', { name: genericMessages.modalEntityRulesAddNewRuleBtnText.defaultMessage });
      userEvent.click(addNewRuleBtn);
    });

    await waitFor(async () => {
      const modal = getByRole('dialog');

      expect(within(modal)
        .getByText(
          genericMessages.modalEntityActionEventNameLabelText.defaultMessage.replace('{eventType}', 'event type'),
        )).toBeInTheDocument();
      const eventTypeInput = within(modal)
        .getByLabelText(genericMessages.modalEntityRulesRuleEventTypeLabel.defaultMessage);
      userEvent.click(eventTypeInput);
      userEvent.tab();
    });

    await waitFor(async () => {
      const modal = getByRole('dialog');
      expect(within(modal)
        .getByText(
          genericMessages.modalEntityValidationActionEventNameRequiredText.defaultMessage,
        )).toBeInTheDocument();
    });

    await waitFor(async () => {
      const modal = getByRole('dialog');
      expect(within(modal)
        .getByText(
          genericMessages.modalEntityActionEventNameLabelText.defaultMessage.replace('{eventType}', 'event type'),
        )).toBeInTheDocument();
      const countInput = within(modal)
        .getByLabelText(genericMessages.modalEntityRulesRuleCountLabel.defaultMessage);
      userEvent.click(countInput);
      userEvent.tab();
    });

    await waitFor(async () => {
      const modal = getByRole('dialog');
      expect(within(modal)
        .getByText(genericMessages.modalEntityValidationActionCountRequiredText.defaultMessage)).toBeInTheDocument();
    });
  });

  it('validates the course filter when adding a new rule', async () => {
    const setModalOpen = jest.fn();

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: false,
      openManageEntityModal: setModalOpen,
    }));

    const { rerender, getByTestId, getByRole } = renderWithProviders(<Badges />);

    const addNewBadgeBtn = getByTestId('add-badge-button');
    userEvent.click(addNewBadgeBtn);

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: true,
      openManageEntityModal: setModalOpen,
    }));

    rerender(<Badges />);

    await waitFor(async () => {
      const modal = getByRole('dialog');
      const addNewRuleBtn = within(modal)
        .getByRole('button', { name: genericMessages.modalEntityRulesAddNewRuleBtnText.defaultMessage });
      userEvent.click(addNewRuleBtn);
    });

    await waitFor(async () => {
      const selectElement = getByTestId('add-filter-select');
      userEvent.selectOptions(selectElement, ['course']);
    });

    await waitFor(async () => {
      const modal = getByRole('dialog');
      const courseSelectField = within(modal)
        .getByText(genericMessages.modalEntityRulesFilterSelectTitle.defaultMessage.replace('{filterName}', 'Course'));
      expect(
        within(modal).getByRole('button', { name: genericMessages.modalEntityRulesBtnRemoveFilterText.defaultMessage }),
      ).toBeInTheDocument();
      userEvent.click(courseSelectField);
      userEvent.tab();
    });

    await waitFor(async () => {
      const modal = getByRole('dialog');
      expect(within(modal).getByText(/course is required/i)).toBeInTheDocument();
    });
  });

  it('validates the organization filter when adding a new rule', async () => {
    const setModalOpen = jest.fn();

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: false,
      openManageEntityModal: setModalOpen,
    }));

    const { rerender, getByTestId, getByRole } = renderWithProviders(<Badges />);

    const addNewBadgeBtn = getByTestId('add-badge-button');
    userEvent.click(addNewBadgeBtn);

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: true,
      openManageEntityModal: setModalOpen,
    }));

    rerender(<Badges />);

    await waitFor(async () => {
      const modal = getByRole('dialog');
      const addNewRuleBtn = within(modal)
        .getByRole('button', { name: genericMessages.modalEntityRulesAddNewRuleBtnText.defaultMessage });
      userEvent.click(addNewRuleBtn);
    });

    await waitFor(async () => {
      const modal = getByRole('dialog');
      const selectElement = within(modal).getByTestId('add-filter-select');
      userEvent.selectOptions(selectElement, ['org']);
    });

    await waitFor(async () => {
      const modal = getByRole('dialog');
      const orgSelectField = within(modal)
        .getByText(
          genericMessages.modalEntityRulesFilterSelectTitle.defaultMessage.replace('{filterName}', 'Organization'),
        );
      expect(
        within(modal).getByRole('button', {
          name: genericMessages.modalEntityRulesBtnRemoveFilterText.defaultMessage,
        }),
      ).toBeInTheDocument();
      userEvent.click(orgSelectField);
      userEvent.tab();
    });

    await waitFor(async () => {
      const modal = getByRole('dialog');
      expect(within(modal).getByText(/org is required/i)).toBeInTheDocument();
    });
  });

  it('validates the frequency filter when adding a new rule', async () => {
    const setModalOpen = jest.fn();

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: false,
      openManageEntityModal: setModalOpen,
    }));

    const { rerender, getByTestId, getByRole } = renderWithProviders(<Badges />);

    const addNewBadgeBtn = getByTestId('add-badge-button');
    userEvent.click(addNewBadgeBtn);

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: true,
      openManageEntityModal: setModalOpen,
    }));

    rerender(<Badges />);

    await waitFor(async () => {
      const modal = getByRole('dialog');
      const addNewRuleBtn = within(modal)
        .getByRole('button', { name: genericMessages.modalEntityRulesAddNewRuleBtnText.defaultMessage });
      userEvent.click(addNewRuleBtn);
    });

    await waitFor(async () => {
      const modal = getByRole('dialog');
      const selectElement = within(modal).getByTestId('add-filter-select');
      userEvent.selectOptions(selectElement, ['frequency']);
    });

    await waitFor(async () => {
      const modal = getByRole('dialog');
      const frequencySelectField = within(modal).getByPlaceholderText('Frequency');
      expect(
        within(modal).getByRole('button', { name: genericMessages.modalEntityRulesBtnRemoveFilterText.defaultMessage }),
      ).toBeInTheDocument();
      userEvent.click(frequencySelectField);
      userEvent.tab();
    });

    await waitFor(async () => {
      const modal = getByRole('dialog');
      expect(
        within(modal).getByText(genericMessages.modalEntityValidationFrequencyPositiveNumberText.defaultMessage),
      ).toBeInTheDocument();
    });
  });

  it('check validation errors when required interval fields are not filled in the badge management modal', async () => {
    const setModalOpen = jest.fn();

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: false,
      openManageEntityModal: setModalOpen,
    }));

    const { rerender, getByTestId, getByRole } = renderWithProviders(<Badges />);

    const addNewBadgeBtn = getByTestId('add-badge-button');
    userEvent.click(addNewBadgeBtn);

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: true,
      openManageEntityModal: setModalOpen,
    }));

    rerender(<Badges />);

    await waitFor(async () => {
      const modal = getByRole('dialog');
      const addNewRuleBtn = within(modal)
        .getByRole('button', { name: genericMessages.modalEntityRulesAddNewRuleBtnText.defaultMessage });
      userEvent.click(addNewRuleBtn);
    });

    await waitFor(async () => {
      const modal = getByRole('dialog');
      const selectElement = within(modal).getByTestId('add-filter-select');
      userEvent.selectOptions(selectElement, ['interval']);
    });

    await waitFor(async () => {
      const modal = getByRole('dialog', { name: moduleMessages.addManageEntityModalTitle.defaultMessage });
      const intervalStartDateDatePicker = within(modal)
        .getByText(genericMessages.modalEntityRulesIntervalStartLabelText.defaultMessage);
      expect(
        within(modal).getByRole('button', { name: genericMessages.modalEntityRulesBtnRemoveFilterText.defaultMessage }),
      ).toBeInTheDocument();
      userEvent.click(intervalStartDateDatePicker);

      const filtersHeading = within(modal).getByRole('heading', {
        level: 2, name: genericMessages.modalEntityRulesFiltersHeadingTitle.defaultMessage,
      });
      userEvent.click(filtersHeading);
    });

    await waitFor(async () => {
      const modal = getByRole('dialog', { name: moduleMessages.addManageEntityModalTitle.defaultMessage });
      expect(within(modal)
        .getByText(genericMessages.modalEntityValidationStartDateRequiredText.defaultMessage)).toBeInTheDocument();
    });

    await waitFor(async () => {
      const modal = getByRole('dialog', { name: moduleMessages.addManageEntityModalTitle.defaultMessage });
      const intervalEndDateDatePicker = within(modal)
        .getByText(genericMessages.modalEntityRulesIntervalEndLabelText.defaultMessage);

      expect(
        within(modal).getByRole('button', { name: genericMessages.modalEntityRulesBtnRemoveFilterText.defaultMessage }),
      ).toBeInTheDocument();
      userEvent.click(intervalEndDateDatePicker);

      const filtersHeading = within(modal).getByRole('heading', {
        level: 2, name: genericMessages.modalEntityRulesFiltersHeadingTitle.defaultMessage,
      });
      userEvent.click(filtersHeading);
    });

    await waitFor(async () => {
      const modal = getByRole('dialog', { name: moduleMessages.addManageEntityModalTitle.defaultMessage });
      expect(within(modal)
        .getByText(/is required/)).toBeInTheDocument();
    });
  });

  it('check show date picker calendar', async () => {
    const setModalOpen = jest.fn();

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: false,
      openManageEntityModal: setModalOpen,
    }));

    const { rerender, getByTestId, getByRole } = renderWithProviders(<Badges />);

    const addNewBadgeBtn = getByTestId('add-badge-button');
    userEvent.click(addNewBadgeBtn);

    useBadges.mockImplementation(() => ({
      badgesData: [],
      isLoading: false,
      isError: false,
      isManageEntityModalOpen: true,
      openManageEntityModal: setModalOpen,
    }));

    rerender(<Badges />);

    await waitFor(async () => {
      const modal = getByRole('dialog');
      const addNewRuleBtn = within(modal)
        .getByRole('button', { name: genericMessages.modalEntityRulesAddNewRuleBtnText.defaultMessage });
      userEvent.click(addNewRuleBtn);
    });

    await waitFor(async () => {
      const modal = getByRole('dialog');
      const selectElement = within(modal).getByTestId('add-filter-select');
      userEvent.selectOptions(selectElement, ['interval']);
    });

    await waitFor(async () => {
      const modal = getByRole('dialog');
      const intervalStartDateDatePicker = within(modal)
        .getByText(genericMessages.modalEntityRulesIntervalStartLabelText.defaultMessage);
      const intervalEndDateDatePicker = within(modal)
        .getByText(genericMessages.modalEntityRulesIntervalEndLabelText.defaultMessage);
      expect(intervalStartDateDatePicker).toBeInTheDocument();
      expect(intervalEndDateDatePicker).toBeInTheDocument();
      expect(
        within(modal).getByRole('button', { name: genericMessages.modalEntityRulesBtnRemoveFilterText.defaultMessage }),
      ).toBeInTheDocument();
      userEvent.click(intervalStartDateDatePicker);
      userEvent.tab();
    });

    await waitFor(async () => {
      const datePickerCalendar = getByRole('dialog', { name: 'Choose Date' });

      daysInTheWeek.forEach((day) => {
        expect(within(datePickerCalendar).getByText(day)).toBeInTheDocument();
      });
    });

    await waitFor(async () => {
      const datePickerCalendar = getByRole('dialog', { name: 'Choose Date' });
      const previousMonthBtn = within(datePickerCalendar).getByRole('button', { name: /Previous Month/i });
      expect(within(datePickerCalendar).getByRole('heading', {
        level: 2, name: /March 2025/i,
      })).toBeInTheDocument();
      userEvent.click(previousMonthBtn);
    });

    await waitFor(async () => {
      const datePickerCalendar = getByRole('dialog', { name: 'Choose Date' });
      expect(within(datePickerCalendar).getByRole('heading', {
        level: 2, name: /February 2025/i,
      })).toBeInTheDocument();
    });
  });
});

describe('fetchBadgesData API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches badge data successfully from API', async () => {
    axios.get.mockResolvedValueOnce({ data: badgesMocks });

    const data = await fetchBadgesData();

    expect(axios.get).toHaveBeenCalledTimes(1);
    expect(axios.get).toHaveBeenCalledWith(API_ROUTES.BADGES);
    expect(convertKeysToSnakeCase(data)).toEqual(badgesMocks);
  });

  it('throws an error when API request fails', async () => {
    axios.get.mockRejectedValueOnce(new Error('Network Error'));

    await expect(fetchBadgesData()).rejects.toThrow('Network Error');
    expect(axios.get).toHaveBeenCalledTimes(1);
    expect(axios.get).toHaveBeenCalledWith(API_ROUTES.BADGES);
  });
});

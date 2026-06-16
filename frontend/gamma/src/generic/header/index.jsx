import React from 'react';
import { useIntl } from 'react-intl';
import { Link } from 'react-router-dom';
import classNames from 'classnames';
import {
  Navbar, Container, Image, Nav,
  Hyperlink, Button, Dropdown, breakpoints, useMediaQuery,
} from '@openedx/paragon';
import { ArrowBack as ArrowBackIcon } from '@openedx/paragon/icons';

import messages from '../../i18n';
import { ROUTES } from '../../routes';
import { getGammaHeaderConfig } from '../../utils';

import Logo from '../../assets/images/logo.svg';

const Header = () => {
  const intl = useIntl();
  const isLargeScreen = useMediaQuery({ maxWidth: breakpoints.large.minWidth });
  const BASE_URL = window.location.origin;

  // The standalone gamma app only knows its own (gamma) origin; the current user
  // and the cross-host LMS/MFE URLs + logo are injected by the Django view.
  const {
    username, lmsBaseUrl, mfeBaseUrl, logoUrl,
  } = getGammaHeaderConfig();

  const routes = [
    {
      path: ROUTES.BADGES,
      label: intl.formatMessage(messages.headerBadgesLinkText),
    },
  ];

  // Per-user navigation dropdown mirroring the menu shown on every other page,
  // so an admin can navigate away from this otherwise-standalone settings app.
  // Built only when the backend supplied the user + LMS base; the MFE group is
  // included only when the MFE base is known. Falls back to a plain sign-out
  // button so the header is never empty (e.g. in local dev / tests).
  const userMenuGroups = (username && lmsBaseUrl) ? [
    [
      { href: `${lmsBaseUrl}/gamma_dashboard/dashboard/`, label: intl.formatMessage(messages.headerUserMenuPerformance) },
      { href: `${lmsBaseUrl}/gamma_dashboard/leaderboard/`, label: intl.formatMessage(messages.headerUserMenuLeaderboard) },
      { href: `${BASE_URL}${ROUTES.APP_BASE_NAME}${ROUTES.BADGES}/`, label: intl.formatMessage(messages.headerUserMenuGamificationSettings) },
    ],
    [
      ...(mfeBaseUrl ? [
        { href: `${mfeBaseUrl}/profile/u/${username}`, label: intl.formatMessage(messages.headerUserMenuPublicProfile) },
        { href: `${mfeBaseUrl}/account/`, label: intl.formatMessage(messages.headerUserMenuAccountSettings) },
      ] : []),
    ],
    [
      { href: `${lmsBaseUrl}/logout`, label: intl.formatMessage(messages.headerBtnSingOutText) },
    ],
  ].filter((group) => group.length) : null;

  return (
    <header className="page-header">
      <Navbar expand="lg">
        <Container size="lg">
          <Navbar.Brand className="p-0 mr-4">
            <Link to={ROUTES.BADGES}>
              <Image
                className="page-header-logo"
                src={logoUrl || Logo}
                alt={intl.formatMessage(messages.headerLogoAltText)}
              />
            </Link>
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="mie-auto">
              {routes?.length && routes.map(({ path, label }) => (
                <Nav.Link
                  className={classNames('page-header-nav-link', { 'text-center': isLargeScreen })}
                  as={Link}
                  key={path}
                  to={path}
                >
                  {label}
                </Nav.Link>
              ))}
            </Nav>
            {userMenuGroups ? (
              <Dropdown>
                <Dropdown.Toggle
                  id="gamma-user-menu"
                  variant="tertiary"
                  size="sm"
                  className={classNames('page-header-user-menu-toggle', { 'w-100': isLargeScreen })}
                  aria-label={intl.formatMessage(messages.headerUserMenuLabel, { username })}
                >
                  {username}
                </Dropdown.Toggle>
                <Dropdown.Menu alignRight>
                  {userMenuGroups.map((group, index) => (
                    <React.Fragment key={group[0].href}>
                      {index > 0 && <Dropdown.Divider />}
                      {group.map(({ href, label }) => (
                        <Dropdown.Item key={href} href={href}>
                          {label}
                        </Dropdown.Item>
                      ))}
                    </React.Fragment>
                  ))}
                </Dropdown.Menu>
              </Dropdown>
            ) : (
              <Button
                className={classNames({ 'w-100': isLargeScreen })}
                as={Hyperlink}
                destination={`${BASE_URL}${ROUTES.ADMIN_LOGOUT}`}
                iconBefore={ArrowBackIcon}
                size="sm"
                variant="tertiary"
              >
                {intl.formatMessage(messages.headerBtnSingOutText)}
              </Button>
            )}
          </Navbar.Collapse>
        </Container>
      </Navbar>
    </header>
  );
};

export default Header;

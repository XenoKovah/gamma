import React from 'react';
import { Link } from 'react-router-dom';
import classNames from 'classnames';
import {
  Navbar, Container, Image, Nav,
  Hyperlink, Button, breakpoints, useMediaQuery,
} from '@openedx/paragon';
import { ArrowBack as ArrowBackIcon } from '@openedx/paragon/icons';

import { useTranslate } from '../../i18n/utils';
import { ROUTES } from './routes';

import Logo from '../../assets/images/logo.svg';

const Header = () => {
  const isLargeScreen = useMediaQuery({ maxWidth: breakpoints.large.minWidth });
  const BASE_URL = window.location.origin;

  const messages = {
    singOutBtnText: useTranslate('generic.header.button.sing.out.text'),
    logoAltText: useTranslate('generic.header.logo.alt.text'),
    routes: {
      badges: useTranslate('generic.header.nav.badges'),
      avatar: useTranslate('generic.header.nav.avatar'),
    },
  };

  const routes = [
    {
      path: ROUTES.BADGES,
      label: messages.routes.badges,
    },
    {
      path: ROUTES.AVATAR,
      label: messages.routes.avatar,
    },
  ];

  return (
    <header className="page-header">
      <Navbar expand="lg">
        <Container size="lg">
          <Navbar.Brand className="p-0 mr-4">
            <Link to={ROUTES.BADGES}>
              <Image className="page-header-logo" src={Logo} alt={messages.logoAltText} />
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
            <Button
              className={classNames({ 'w-100': isLargeScreen })}
              as={Hyperlink}
              destination={`${BASE_URL}${ROUTES.ADMIN_LOGOUT}`}
              iconBefore={ArrowBackIcon}
              size="sm"
              variant="tertiary"
            >
              {messages.singOutBtnText}
            </Button>
          </Navbar.Collapse>
        </Container>
      </Navbar>
    </header>
  );
};

export default Header;

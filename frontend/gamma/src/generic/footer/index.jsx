import React from 'react';
import { Link } from 'react-router-dom';
import { Navbar, Container, Image } from '@openedx/paragon';

import { useTranslate } from '../../i18n/utils';

import Logo from '../../assets/images/logo.svg';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const messages = {
    logoAltText: useTranslate('generic.header.logo.alt.text'),
  };

  return (
    <footer className="page-footer">
      <Navbar expand="lg">
        <Container size="lg">
          <Navbar.Brand className="p-0 mr-4">
            <Link to="/badges">
              <Image className="page-footer-logo" src={Logo} alt={messages.logoAltText} />
            </Link>
          </Navbar.Brand>
          <span className="page-footer-copy">
            &copy; {currentYear}
          </span>
        </Container>
      </Navbar>
    </footer>
  );
};

export default Footer;

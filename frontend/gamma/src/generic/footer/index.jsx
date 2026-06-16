import React from 'react';
import { useIntl } from 'react-intl';
import { Link } from 'react-router-dom';
import { Navbar, Container, Image } from '@openedx/paragon';

import messages from '../../i18n';
import { ROUTES } from '../../routes';
import { getGammaHeaderConfig } from '../../utils';

import Logo from '../../assets/images/logo.svg';

const Footer = () => {
  const intl = useIntl();
  const currentYear = new Date().getFullYear();
  const { logoUrl } = getGammaHeaderConfig();

  return (
    <footer className="page-footer">
      <Navbar expand="lg">
        <Container size="lg">
          <Navbar.Brand className="p-0 mr-4">
            <Link to={ROUTES.BADGES}>
              <Image
                className="page-footer-logo"
                src={logoUrl || Logo}
                alt={intl.formatMessage(messages.headerLogoAltText)}
              />
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

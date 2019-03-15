import React from 'react';
import {getCookie} from '../Utils';

const BADGE_RULES = '/api/v0/badge-rules/';
const ACTIONS = '/api/v0/actions';
const COURSES = '/api/v0/courses';
const ORGANISATIONS = '/api/v0/organizations';

const HEADERS = {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')};

export {BADGE_RULES, ACTIONS, COURSES, HEADERS, ORGANISATIONS};

import {getCookie} from '../Utils';

const BADGE_RULES = '/api/v0/badge-rules/';
const ACTIONS = '/api/v0/actions/';
const COURSES = '/api/v0/courses/';
const ORGANISATIONS = '/api/v0/organizations/';
const LEADERBOARD = '/api/v0/leaderboard/';

const HEADERS = {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')};

function getRules(slug) {
    return fetch(
                BADGE_RULES + `?slug=${slug}`,{
                    credentials: 'same-origin'
                }
                )
            .then(res => res.json());
}

export {BADGE_RULES, ACTIONS, COURSES, HEADERS, ORGANISATIONS, getRules, LEADERBOARD};

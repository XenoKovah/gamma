const AllowedFilters = ['org', 'frequency', 'interval', 'course'];

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

function isObjectEmpty(object) {
    for (let key in object) {
        if (!object[key]){return true}
        return false;
    }
    return true;
}

// Create new new object and populate it with not empty values
// Don't worth trying to understand it, it relies only on known data structure
function validateObjects(object) {
    let newObject = {};
    for (let key in object) {
        if (typeof object[key] === 'object') {
            for (let _key in object[key]) {
                if (typeof object[key][_key] === 'object') {
                    for (let __key in object[key][_key]) {
                        if (Boolean(object[key][_key][__key])) {
                            newObject[key][_key] = newObject[key][_key] || {};
                            newObject[key][_key][__key] = object[key][_key][__key];
                        }
                    }
                } else if (Boolean(object[key][_key])) {
                    newObject[key] = newObject[key] || {};
                    newObject[key][_key] = object[key][_key];
                }
            }
        } else {
            if (Boolean(object[key])) {
                newObject[key] = object[key];
            }
        }
    }
    return newObject;
}

// The function takes a course as a string in the format of "course-v1:edX+Demo_Course+2023"
// Returns a string containing the org name or null if the course format does not match the pattern.
function getOrgFromCourseKey(courseKey) {
    const regex = /^course-v1:([^+]+)/;
    const result = regex.exec(courseKey)
    return result ? result[1] : null;
}

export {AllowedFilters, getCookie, isObjectEmpty, validateObjects, getOrgFromCourseKey};

import { getOrgFromCourseKey } from '../Utils';

describe('test the function of getting an organization from a course key', () => {
    it('should extract organization name from course key if course key is valid', () => {
        const courseKey = 'course-v1:edX+Demo_Course+2023';
        const org = getOrgFromCourseKey(courseKey);

        expect(org).toEqual('edX');
    });

    it('should return null if course key is invalid', () => {
        const courseKey = 'invalid-course-key';
        const org = getOrgFromCourseKey(courseKey);

        expect(org).toBeNull();
    });
});

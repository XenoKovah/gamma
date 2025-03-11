import axios from 'axios';
import {
  fetchAvatarSetsData,
  deleteAvatarSet,
  createAvatarSet,
  updateAvatarSet,
  finishUpdatingAvatarSet,
  deleteAvatarById,
  updateAvatarById,
  fetchCoursesData,
  fetchOrganizationsData,
  fetchActionsData,
} from '../api';

jest.mock('axios');

describe('API functions', () => {
  beforeAll(() => {
    global.structuredClone = (obj) => JSON.parse(JSON.stringify(obj));
  });

  describe('fetchAvatarSetsData', () => {
    it('should fetch avatar sets and process them', async () => {
      const mockData = [{ id: 1, title: 'Avatar Set 1', avatars: [] }];
      axios.get.mockResolvedValue({ data: mockData });

      const result = await fetchAvatarSetsData();
      expect(result).toEqual(expect.any(Array));
    });
  });

  describe('deleteAvatarSet', () => {
    it('should delete an avatar set by ID', async () => {
      axios.delete.mockResolvedValue({ data: { success: true } });
      const result = await deleteAvatarSet(1);
      expect(result).toEqual({ success: true });
    });
  });

  describe('createAvatarSet', () => {
    it('should create a new avatar set', async () => {
      const mockData = { id: 1, title: 'New Avatar Set' };
      axios.post.mockResolvedValue({ data: mockData });

      const result = await createAvatarSet(mockData);
      expect(result).toEqual(expect.objectContaining({ id: 1 }));
    });
  });

  describe('updateAvatarSet', () => {
    it('should update an avatar set', async () => {
      const mockData = { id: 1, title: 'Updated Avatar Set', avatars: [] };
      axios.patch.mockResolvedValue({ data: mockData });

      const result = await updateAvatarSet(mockData);
      expect(result).toEqual(expect.objectContaining({ title: 'Updated Avatar Set' }));
    });
  });

  describe('finishUpdatingAvatarSet', () => {
    it('should mark an avatar set as finished updating', async () => {
      axios.patch.mockResolvedValue({ data: { success: true } });

      const result = await finishUpdatingAvatarSet(1);
      expect(result).toEqual({ success: true });
    });
  });

  describe('deleteAvatarById', () => {
    it('should delete an avatar by ID', async () => {
      axios.delete.mockResolvedValue({ data: { success: true } });
      const result = await deleteAvatarById(1);
      expect(result).toEqual({ success: true });
    });
  });

  describe('updateAvatarById', () => {
    it('should update an avatar by ID', async () => {
      const mockData = { id: 1, title: 'Updated Avatar' };
      axios.patch.mockResolvedValue({ data: mockData });

      const result = await updateAvatarById(1, mockData);
      expect(result).toEqual(expect.objectContaining({ title: 'Updated Avatar' }));
    });
  });

  describe('fetchCoursesData', () => {
    it('should fetch courses data', async () => {
      const mockData = [{ id: 1, name: 'Course 1' }];
      axios.get.mockResolvedValue({ data: mockData });

      const result = await fetchCoursesData();
      expect(result).toEqual(mockData);
    });
  });

  describe('fetchOrganizationsData', () => {
    it('should fetch organizations data', async () => {
      const mockData = [{ id: 1, name: 'Organization 1' }];
      axios.get.mockResolvedValue({ data: mockData });

      const result = await fetchOrganizationsData();
      expect(result).toEqual(mockData);
    });
  });

  describe('fetchActionsData', () => {
    it('should fetch actions data', async () => {
      const mockData = [{ id: 1, type: 'Click' }];
      axios.get.mockResolvedValue({ data: mockData });

      const result = await fetchActionsData();
      expect(result).toEqual(mockData);
    });
  });
});

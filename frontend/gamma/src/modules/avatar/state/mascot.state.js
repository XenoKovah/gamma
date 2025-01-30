import { create } from 'zustand';

import axiosInstance from '../apis/axios';
import { apis } from '../apis/urls';
import { findSelectedItemThroughId, getDefaultItem } from '../helpers/functions';

const {
  fetchMascotItems,
  fetchSelectedMascotItems,
  createUserMascot,
  updateUserMascot,
} = apis;

const initializer = (set, get) => ({
  colors: [],
  headdress: [],
  outerwear: [],
  glasses: [],
  emotion: [],
  selectedMascotData: null,
  isMascotUpdating: false,
  isLoading: false,
  canvasImgUrl: '',

  setCanvasImgUrl: (canvasImgUrl) => {
    set({
      canvasImgUrl,
    });
  },

  setIsMascotUpdating: (isMascotUpdating) => set({ isMascotUpdating }),

  setIsLoading: (isLoading) => set({ isLoading }),

  fetchMascotItems: async () => {
    set({ isLoading: true });

    const fetchSelectedMascotItemsFn = get().fetchSelectedMascotItems;

    try {
      const response = await axiosInstance.get(fetchMascotItems);

      const { data } = response;

      set({
        isLoading: false,
        // for showing all available items
        ...data,
      });
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Error fetching user mascot data: ', error);

      set({ isLoading: false });
    } finally {
      await fetchSelectedMascotItemsFn();
    }
  },

  fetchSelectedMascotItems: async () => {
    set({ isLoading: true });

    const {
      colors,
      glasses,
      headdress,
      outerwear,
      emotion,
      setSelectedMascotData,
    } = get();

    try {
      const response = await axiosInstance.get(fetchSelectedMascotItems);

      const {
        color,
        glasses: glassesId,
        headdress: headdressId,
        outerwear: outerwearId,
        emotion: emotionId,
        // eslint-disable-next-line camelcase
        use_mascot,
      } = response.data;

      set({
        isLoading: false,
        // indicates if mascot was already created
        isMascotUpdating: true,
      });

      setSelectedMascotData({
        colors: findSelectedItemThroughId(color, colors),
        glasses: findSelectedItemThroughId(glassesId, glasses),
        headdress: findSelectedItemThroughId(headdressId, headdress),
        outerwear: findSelectedItemThroughId(outerwearId, outerwear),
        emotion: findSelectedItemThroughId(emotionId, emotion),
        // eslint-disable-next-line camelcase
        use_mascot,
      });
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Error fetching user mascot data: ', error);
      set({
        isLoading: false,
        // indicates if mascot was already created
        isMascotUpdating: false,
      });

      // set default items, in fetchSelectedMascotItems they will be override
      setSelectedMascotData({
        colors: getDefaultItem(colors),
        glasses: getDefaultItem(glasses),
        emotion: getDefaultItem(emotion),
        headdress: getDefaultItem(headdress),
        outerwear: getDefaultItem(outerwear),
        use_mascot: false,
      });
    }
  },

  createMascot: async () => {
    set({ isLoading: true });

    const { selectedMascotData, canvasImgUrl } = get();

    if (!selectedMascotData) {
      // eslint-disable-next-line no-console
      console.error('No selected mascot data available');
      set({ isLoading: false });

      return;
    }

    const {
      colors,
      // eslint-disable-next-line camelcase
      use_mascot,
      glasses,
      headdress,
      outerwear,
      emotion,
    } = selectedMascotData;

    try {
      const response = await fetch(canvasImgUrl);
      const blob = await response.blob();

      const formData = new FormData();
      formData.append('image', blob, 'mascot.png');
      formData.append('mascot_data', JSON.stringify({
        ...(colors?.id ? { color_id: colors.id } : {}),
        ...(glasses?.id ? { glasses_id: glasses.id } : {}),
        ...(headdress?.id ? { headdress_id: headdress.id } : {}),
        ...(outerwear?.id ? { outerwear_id: outerwear.id } : {}),
        ...(emotion?.id ? { emotion_id: emotion.id } : {}),
        // eslint-disable-next-line camelcase
        use_mascot,
      }));

      await axiosInstance.post(createUserMascot, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Error on createMascot: ', error);
    } finally {
      set({ isLoading: false });
    }
  },

  updateMascot: async () => {
    set({ isLoading: true });

    const { selectedMascotData, canvasImgUrl } = get();

    if (!selectedMascotData) {
      // eslint-disable-next-line no-console
      console.error('No selected mascot data available');
      set({ isLoading: false });

      return;
    }

    const {
      colors,
      // eslint-disable-next-line camelcase
      use_mascot,
      glasses,
      headdress,
      outerwear,
      emotion,
    } = selectedMascotData;

    try {
      const response = await fetch(canvasImgUrl);
      const blob = await response.blob();

      const formData = new FormData();
      formData.append('image', blob, 'mascot.png');
      formData.append('mascot_data', JSON.stringify({
        ...(colors?.id ? { color_id: colors.id } : {}),
        ...(glasses?.id ? { glasses_id: glasses.id } : {}),
        ...(headdress?.id ? { headdress_id: headdress.id } : {}),
        ...(outerwear?.id ? { outerwear_id: outerwear.id } : {}),
        ...(emotion?.id ? { emotion_id: emotion.id } : {}),
        // eslint-disable-next-line camelcase
        use_mascot,
      }));

      await axiosInstance.post(updateUserMascot, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      window.location.assign(`${window.location.href}?tab=tab5&sub-tab=sub-tab7`);
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Error on updateMascot: ', error);
    } finally {
      set({ isLoading: false });
    }
  },

  setSelectedMascotData: (data) => {
    const { selectedMascotData } = get();

    set({
      selectedMascotData: {
        ...selectedMascotData,
        ...data,
      },
    });
  },
});

export const useMascotStore = create()(initializer);

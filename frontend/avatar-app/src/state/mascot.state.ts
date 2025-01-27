import { create, StateCreator } from "zustand";
import { ICommon, IMascotColors, IMascotItems, IMascotItemsByCategories, IMascotState } from "../interfaces/interfaces";
import axiosInstance from "../apis/axios";
import { apis } from "../apis/urls";
import { findSelectedItemThroughId, getDefaultItem } from "../helpers/functions";

const {
  fetchMascotItems,
  fetchSelectedMascotItems,
  createUserMascot,
  updateUserMascot,
} = apis;

const initializer: StateCreator<IMascotState> = (set, get) => ({
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
      canvasImgUrl
    });
  },

  setIsMascotUpdating: (isMascotUpdating: boolean) => set({ isMascotUpdating }),

  setIsLoading: (isLoading: boolean) => set({ isLoading }),

  fetchMascotItems: async () => {
    set({ isLoading: true });

    const { fetchSelectedMascotItems } = get();

    try {
      const response = await axiosInstance.get(fetchMascotItems);

      const data = response.data;

      set({
        isLoading: false,
        // for showing all available items
        ...data,
      });
    } catch (error) {
      console.error("Error fetching user mascot data: ", error);
      set({ isLoading: false });
    } finally {
      await fetchSelectedMascotItems()
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
        use_mascot,
      } = response.data;

      set({
        isLoading: false,
        // indicates if mascot was already created
        isMascotUpdating: true,
      });

      setSelectedMascotData({
        colors: findSelectedItemThroughId(color, colors) as IMascotColors,
        glasses: findSelectedItemThroughId(glassesId, glasses) as IMascotItems,
        headdress: findSelectedItemThroughId(headdressId, headdress) as IMascotItems,
        outerwear: findSelectedItemThroughId(outerwearId, outerwear) as IMascotItems,
        emotion: findSelectedItemThroughId(emotionId, emotion) as IMascotItems,
        use_mascot,
      })
    } catch (error) {
      console.error("Error fetching user mascot data: ", error);
      set({
        isLoading: false,
        // indicates if mascot was already created
        isMascotUpdating: false,
      });

      // set default items, in fetchSelectedMascotItems they will be override
      setSelectedMascotData({
        colors: getDefaultItem(colors) as IMascotColors,
        glasses: getDefaultItem(glasses) as IMascotItems,
        emotion: getDefaultItem(emotion) as IMascotItems,
        headdress: getDefaultItem(headdress) as IMascotItems,
        outerwear: getDefaultItem(outerwear) as IMascotItems,
        use_mascot: false,
      })
    }
  },

  createMascot: async () => {
    set({ isLoading: true });

    const { selectedMascotData, canvasImgUrl } = get();

    if (!selectedMascotData) {
      console.error("No selected mascot data available");
      set({ isLoading: false });

      return;
    }

    const {
      colors,
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
        use_mascot,
      }));

      await axiosInstance.post(createUserMascot, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });
    } catch (error) {
      console.error("Error on createMascot: ", error);
    } finally {
      set({ isLoading: false });
    }
  },

  updateMascot: async () => {
    set({ isLoading: true });

    const { selectedMascotData, canvasImgUrl } = get();

    if (!selectedMascotData) {
      console.error("No selected mascot data available");
      set({ isLoading: false });

      return;
    }

    const {
      colors,
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
        use_mascot,
      }));

      await axiosInstance.post(updateUserMascot, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });
      window.location.assign(window.location.href + '?tab=tab5&sub-tab=sub-tab7');
    } catch (error) {
      console.error("Error on updateMascot: ", error);
    } finally {
      set({ isLoading: false });
    }
  },

  setSelectedMascotData: (data) => {
    const { selectedMascotData } = get();

    set({
      selectedMascotData: {
        ...selectedMascotData,
        ...data
      }
    });
  },
});

export const useMascotStore = create<IMascotState>()(initializer);

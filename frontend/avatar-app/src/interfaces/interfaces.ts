export interface ICommon {
  id: number;
  name: string;
  use_as_default: boolean;
}

export interface IMascotColors extends ICommon{
  hex_color: string;
}

export interface IMascotItems extends ICommon{
  svg_file: string;
}

export interface IMascotItemsByCategories {
  colors: IMascotColors[];
  headdress: IMascotItems[];
  outerwear: IMascotItems[];
  glasses: IMascotItems[];
  emotion: IMascotItems[];
}

interface ISelectedMascotData {
  colors?: IMascotColors;
  headdress?: IMascotItems;
  outerwear?: IMascotItems;
  glasses?: IMascotItems;
  emotion?: IMascotItems;
  use_mascot?: boolean,
}

export interface IMascotState extends IMascotItemsByCategories {
  fetchMascotItems: () => Promise<void>;
  fetchSelectedMascotItems: () => Promise<void>;
  createMascot: () => Promise<void>;
  updateMascot: () => Promise<void>;

  canvasImgUrl: string;
  setCanvasImgUrl: (value: string) => void;

  isMascotUpdating: boolean;
  setIsMascotUpdating: (value: boolean) => void;

  selectedMascotData: ISelectedMascotData | null;
  setSelectedMascotData: (data: Partial<ISelectedMascotData>) => void;

  isLoading: boolean;
  setIsLoading: (isLoading: boolean) => void;
}

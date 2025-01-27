import { useEffect } from "react";
import { useMascotStore } from "../state/mascot.state";
import { loadSvgWithColor } from "../helpers/loadSvgWithColor";
import { getMinimumRatio } from "../helpers/functions";

interface Props {
  canvasRef: React.RefObject<HTMLCanvasElement>;
  color: string;
}

export const mainStarUrl = '/static/avatar-app/images/stars/star_main.svg';

export const useDrawCanvasHook = ({canvasRef, color}: Props) => {
  const {setCanvasImgUrl, selectedMascotData, setSelectedMascotData, fetchMascotItems} = useMascotStore()

  useEffect(() => {
    fetchMascotItems();
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    const cap = selectedMascotData?.headdress?.svg_file
    const emotion = selectedMascotData?.emotion?.svg_file
    const cloth = selectedMascotData?.outerwear?.svg_file
    const glasses = selectedMascotData?.glasses?.svg_file

    if (!canvas) {
      return;
    }

    const ctx = canvas.getContext('2d');
    const ratio = getMinimumRatio();
    canvas.width = 387 * ratio;
    canvas.height = 442 * ratio;

    canvas.style.width = '387px';
    canvas.style.height = '442px';

    ctx?.scale(ratio, ratio);

    const drawImage = async () => {
      ctx?.clearRect(0, 0, canvas.width, canvas.height);

      const {
        image: starImage,
        originalWidth: starOriginalWidth,
        originalHeight: starOriginalHeight
      } = await loadSvgWithColor(mainStarUrl, color);

      ctx?.drawImage(starImage, 0, 0, starOriginalWidth, starOriginalHeight);

      if (cap) {
        const {
          image: capImage,
          originalWidth: capOriginalWidth,
          originalHeight: capOriginalHeight
        } = await loadSvgWithColor(cap, '');

        ctx?.drawImage(capImage, 0, 0, capOriginalWidth, capOriginalHeight);

      }

      if (emotion) {
        const {
          image,
          originalWidth,
          originalHeight
        } = await loadSvgWithColor(emotion, '');

        ctx?.drawImage(image, 0, 0, originalWidth, originalHeight);

      }

      if (cloth) {
        const {
          image,
          originalWidth,
          originalHeight
        } = await loadSvgWithColor(cloth, '');

        ctx?.drawImage(image, 0, 0, originalWidth, originalHeight);
      }

      if (glasses) {
        const {
          image,
          originalWidth,
          originalHeight
        } = await loadSvgWithColor(glasses, '');

        ctx?.drawImage(image, 0, 0, originalWidth, originalHeight);
      }

      setCanvasImgUrl(canvas.toDataURL('image/png'))
    };

    drawImage();
  }, [ color, selectedMascotData, setSelectedMascotData ]);

}

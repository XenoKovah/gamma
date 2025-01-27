import React, { useEffect, useRef, useState } from "react";
import { getMinimumRatio } from "../../helpers/functions";
import { loadSvgWithColor } from "../../helpers/loadSvgWithColor";
import { mainStarUrl } from "../../hooks/useDrawCanvasHook";
import { IMascotItems } from "../../interfaces/interfaces";
import { useMascotStore } from "../../state/mascot.state";

interface Props {
  item: IMascotItems,
  dataKey: string
}

const DrawMascotItem = ({ item, dataKey }: Props) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [ canvasImgUrl, setCanvasImgUrl ] = useState('');
  const { colors } = useMascotStore()


  useEffect(() => {
    const canvas = canvasRef.current;

    if (!canvas) {
      return;
    }

    const ctx = canvas.getContext('2d');
    const ratio = getMinimumRatio();

    canvas.width = 100 * ratio;
    canvas.height = 100 * ratio;

    canvas.style.width = '100px';
    canvas.style.height = '100px';

    ctx?.scale(ratio, ratio);

    const drawImage = async () => {
      ctx?.clearRect(0, 0, canvas.width, canvas.height);

      const isImageNotEmpty= !!item.svg_file

      const {
        image: starImage,
      } = await loadSvgWithColor(mainStarUrl, colors[0].hex_color);

      ctx?.drawImage(starImage, 0, 0, 100, 100);

      if (isImageNotEmpty) {
        const {
          image: itemImage,
        } = await loadSvgWithColor(item.svg_file, '');

        ctx?.drawImage(itemImage, 0, 0, 100, 100);
      }

      setCanvasImgUrl(canvas.toDataURL('image/png'));
    };

    drawImage();
  }, [ item, colors ]);


  return (
    <>
      <canvas ref={canvasRef} style={{ display: 'none' }}/>

      <img src={canvasImgUrl} alt={`${dataKey}_id_${item.id}`}/>
    </>
  );
};

export default DrawMascotItem;

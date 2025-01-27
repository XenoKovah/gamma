import { ICommon, IMascotColors, IMascotItems } from "../interfaces/interfaces";

export const getMinimumRatio = () => {
  const ratio = window.devicePixelRatio || 1;

  return ratio === 1 ? 2 : ratio;
};

export const scaleImage = (
  originalWidth: number,
  originalHeight: number,
  widthMatch: RegExpMatchArray | null,
  heightMatch: RegExpMatchArray | null,
  viewBoxMatch: RegExpMatchArray | null,
  svgText: string,
  svgOpeningTag: string,
) => {
  // Handle scaling and replacements
  const scale = 2;
  const scaledWidth = originalWidth * scale;
  const scaledHeight = originalHeight * scale;
  let updatedSvgText = svgText;

  if (widthMatch && heightMatch) {
    updatedSvgText = updatedSvgText.replace(/width="[\d.]+"/, `width="${scaledWidth}"`);
    updatedSvgText = updatedSvgText.replace(/height="[\d.]+"/, `height="${scaledHeight}"`);
  } else if (viewBoxMatch) {
    console.log('scaledHeight', scaledHeight);
    console.log('scaledWidth', scaledWidth);

    const newViewBox = `0 0 ${scaledWidth} ${scaledHeight}`;
    updatedSvgText = updatedSvgText.replace(/viewBox="\d+\s+\d+\s+[\d.]+\s+[\d.]+"/, `viewBox="${newViewBox}" width="${scaledWidth}" height="${scaledHeight}"`);
  } else {
    // Add width and height if they do not exist directly to the SVG opening tag
    svgOpeningTag = svgOpeningTag.replace(/<svg/, `<svg width="${scaledWidth}" height="${scaledHeight}"`);
    updatedSvgText = updatedSvgText.replace(/<svg [^>]*>/, svgOpeningTag);
  }

  return updatedSvgText;
}

export const getDefaultItem = (array: ICommon[]) => {
  return array.find((item)=>item.use_as_default)
}

export const findSelectedItemThroughId = (id: number, array: ICommon[]) => {
  return array.find((item)=>item.id === id)
}

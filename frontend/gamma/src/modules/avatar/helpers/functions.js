export const getMinimumRatio = () => {
  const ratio = window.devicePixelRatio || 1;

  return ratio === 1 ? 2 : ratio;
};

export const scaleImage = (
  originalWidth,
  originalHeight,
  widthMatch,
  heightMatch,
  viewBoxMatch,
  svgText,
  svgOpeningTag,
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
    const newViewBox = `0 0 ${scaledWidth} ${scaledHeight}`;
    updatedSvgText = updatedSvgText.replace(/viewBox="\d+\s+\d+\s+[\d.]+\s+[\d.]+"/, `viewBox="${newViewBox}" width="${scaledWidth}" height="${scaledHeight}"`);
  } else {
    // Use a new variable instead of reassigning the parameter
    const updatedSvgOpeningTag = svgOpeningTag.replace(/<svg/, `<svg width="${scaledWidth}" height="${scaledHeight}"`);
    updatedSvgText = updatedSvgText.replace(/<svg [^>]*>/, updatedSvgOpeningTag);
  }

  return updatedSvgText;
};

export const getDefaultItem = (array) => array.find((item) => item.use_as_default);

export const findSelectedItemThroughId = (id, array) => array.find((item) => item.id === id);

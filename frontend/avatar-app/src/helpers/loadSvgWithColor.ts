import { scaleImage } from "./functions";

export const loadSvgWithColor = async (svgUrl: string, color: string): Promise<{
  image: CanvasImageSource,
  originalWidth: number,
  originalHeight: number
}> => {
  const svgResponse = await fetch(svgUrl);
  let svgText = await svgResponse.text();

  // Extracting SVG opening tag to limit the scope of width and height search
  const svgOpeningTagMatch = svgText.match(/<svg [^>]*>/);
  let svgOpeningTag = svgOpeningTagMatch ? svgOpeningTagMatch[0] : '';

  // Searching within the SVG opening tag for width and height
  let originalWidth = 0, originalHeight = 0;
  const widthMatch = svgOpeningTag.match(/width="([\d.]+)"/);
  const heightMatch = svgOpeningTag.match(/height="([\d.]+)"/);
  const viewBoxMatch = svgOpeningTag.match(/viewBox="\d+\s+\d+\s+([\d.]+)\s+([\d.]+)"/);

  if (widthMatch && heightMatch) {
    originalWidth = parseFloat(widthMatch[1]);
    originalHeight = parseFloat(heightMatch[1]);
  } else if (viewBoxMatch) {
    originalWidth = parseFloat(viewBoxMatch[1]);
    originalHeight = parseFloat(viewBoxMatch[2]);
  } else {
    throw new Error('SVG dimensions could not be determined.');
  }

  // Handle scaling image, need to FIX it and TEST is first
  // svgText = scaleImage(originalWidth,
  //   originalHeight,
  //   widthMatch,
  //   heightMatch,
  //   viewBoxMatch,
  //   svgText,
  //   svgOpeningTag,)

  // for better image shape
  svgText = svgText.replace(/<path/g, '<path shape-rendering="geometricPrecision"');

  // for changing image color shape
  if (color) {
    svgText = svgText.replace(/(class="replaceable-color".*?fill=")(.*?)"/g, `$1${color}"`);
  }

  return new Promise(resolve => {
    const img = new Image();
    const blob = new Blob([ svgText ], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    img.onload = () => resolve({ image: img, originalHeight, originalWidth });
    img.src = url;
  });
}

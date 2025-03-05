/**
 * Reads a file and returns its contents as a Base64-encoded data URL.
 *
 * @param {File} file - The file to read.
 * @returns {Promise<string>} A promise that resolves with the Base64 data URL of the file.
 */
export const readFileAsDataURL = (file) => new Promise((resolve, reject) => {
  const reader = new FileReader();

  reader.onloadend = () => resolve(reader.result);
  reader.onerror = () => reject(new Error('File reading failed'));

  reader.readAsDataURL(file);
});

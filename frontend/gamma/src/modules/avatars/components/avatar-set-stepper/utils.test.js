import { readFileAsDataURL } from './utils';

describe('readFileAsDataURL', () => {
  it('should read a file and return a Base64 data URL', async () => {
    const file = new File(['dummy content'], 'test.txt', { type: 'text/plain' });

    const result = await readFileAsDataURL(file);

    expect(result).toMatch(/^data:text\/plain;base64,/);
  });

  it('should reject with an error when file reading fails', async () => {
    const file = new File(['dummy content'], 'test.txt', { type: 'text/plain' });

    jest.spyOn(FileReader.prototype, 'readAsDataURL').mockImplementationOnce(function readAsDataURLMock() {
      this.onerror(new Event('error'));
    });

    await expect(readFileAsDataURL(file)).rejects.toThrow('File reading failed');
  });
});

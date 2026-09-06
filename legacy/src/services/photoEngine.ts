import { PhotoFilterSettings } from '../types';

export const DEFAULT_PHOTO_FILTERS: PhotoFilterSettings = {
  brightness: 100,
  contrast: 100,
  saturation: 100,
  blur: 0,
  sepia: 0,
  hueRotate: 0,
  grayscale: 0,
  invert: 0
};

export function getCssFilterString(filters: PhotoFilterSettings): string {
  return [
    `brightness(${filters.brightness}%)`,
    `contrast(${filters.contrast}%)`,
    `saturate(${filters.saturation}%)`,
    `blur(${filters.blur}px)`,
    `sepia(${filters.sepia}%)`,
    `hue-rotate(${filters.hueRotate}deg)`,
    `grayscale(${filters.grayscale}%)`,
    `invert(${filters.invert}%)`
  ].join(' ');
}

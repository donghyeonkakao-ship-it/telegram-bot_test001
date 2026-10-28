// 모든 색은 이 파일에서만 정의한다. 다른 파일에 hex를 직접 쓰지 않는다.
// PaletteColor는 브랜드 타입이라 definePalette를 거치지 않은 문자열은 그리기 함수에 넘길 수 없다.

export type PaletteColor = string & { readonly __brand: 'PaletteColor' };

const HEX = /^#[0-9a-f]{6}$/i;

function definePalette<K extends string>(
  name: string,
  colors: Record<K, string>,
  { min = 8, max = 16 }: { min?: number; max?: number } = {},
): Readonly<Record<K, PaletteColor>> {
  const entries = Object.entries(colors) as [K, string][];
  if (entries.length < min || entries.length > max) {
    throw new Error(`palette "${name}": ${entries.length}색 (허용 ${min}~${max}색)`);
  }
  for (const [key, hex] of entries) {
    if (!HEX.test(hex)) throw new Error(`palette "${name}.${key}": 잘못된 hex "${hex}"`);
  }
  return Object.freeze(colors as Record<K, PaletteColor>);
}

/** 장면: nether_bar (용암 동굴) */
export const nether = definePalette('nether', {
  void: '#0c0407',
  mortar: '#1c080b',
  brickDark: '#2c0e12',
  brickMid: '#3f1518',
  brickLight: '#5a2220',
  lavaDark: '#8c1d0b',
  lavaMid: '#d8480f',
  lavaLight: '#f59f00',
  lavaHot: '#ffe36e',
  stoneDark: '#4b4a54',
  stoneMid: '#6e6d78',
  stoneLight: '#a3a2ad',
  greenDark: '#237a36',
  green: '#4fcb62',
  greenLight: '#b4f2bc',
  white: '#f6f4ee',
});

/** 픽셀 캔버스 바깥 1280x720 레이어(자막, 워터마크)용 */
export const ui = definePalette(
  'ui',
  {
    subtitleFill: '#ffffff',
    subtitleStroke: '#000000',
    watermark: '#ffffff',
    background: '#000000',
  },
  { min: 1 },
);

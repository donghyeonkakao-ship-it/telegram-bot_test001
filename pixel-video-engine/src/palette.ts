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

/**
 * 장면: nether_bar (Minecraft 네더). 16색으로 블록·몹·UI를 모두 그린다.
 * 한 색이 여러 용도를 겸한다 (예: lavaHot = 용암 하이라이트·발광석·블레이즈 머리).
 */
export const nether = definePalette('nether', {
  black: '#000000', // 외곽선, 눈, 이름표 배경
  shadow: '#3f3f3f', // Minecraft 글자 그림자(흰색의 1/4), 조약돌 틈, 연기
  stone: '#7a7a7a', // 조약돌
  stoneLight: '#adadad', // 조약돌 밝은 면, 휩쓸기 파티클
  white: '#ffffff', // 글자, 검 하이라이트, 눈 흰자
  rackDark: '#3a1111', // 네더랙 어두운 점, 먼 벽
  rack: '#6b2929', // 네더랙 기본, 검 손잡이, 발광석 틈
  rackLight: '#8f423e', // 네더랙 밝은 점
  lavaDark: '#b0360a',
  lava: '#e2680f',
  lavaLight: '#fcaa2e', // 용암 밝은 줄, 발광석, 블레이즈 막대
  lavaHot: '#fff17a', // 용암 최고온, 발광석 하이라이트, 블레이즈 머리
  emeraldDark: '#0b873a', // 에메랄드 블록 그늘, 주인공 머리 그늘
  emerald: '#2fd468', // 에메랄드 블록, 주인공 피부
  emeraldLight: '#a6f6c1', // 에메랄드 블록 하이라이트, 행복 파티클
  diamond: '#4ce6d4', // 다이아몬드 검, 주인공 셔츠
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

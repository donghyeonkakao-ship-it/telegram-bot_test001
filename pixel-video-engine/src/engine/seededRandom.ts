// 시드 기반 난수. Math.random은 금지(Remotion은 프레임을 병렬·비순차로 렌더링한다).

/** mulberry32: 같은 seed면 항상 같은 수열 */
export function createRng(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** 상태 없는 정수 해시 → [0, 1). 프레임·좌표로 바로 값을 뽑을 때 쓴다. */
export function hash01(...ints: number[]): number {
  let h = 0x811c9dc5;
  for (const n of ints) {
    h ^= Math.floor(n) | 0;
    h = Math.imul(h, 0x01000193);
    h ^= h >>> 13;
    h = Math.imul(h, 0x5bd1e995);
    h ^= h >>> 15;
  }
  return (h >>> 0) / 4294967296;
}

/** seed로 고정된 n개의 요소를 만든다. 모듈 최상단에서 한 번 만들어 두고 매 프레임 재사용. */
export function seededList<T>(seed: number, n: number, make: (rng: () => number, i: number) => T): T[] {
  const rng = createRng(seed);
  return Array.from({ length: n }, (_, i) => make(rng, i));
}

export function randInt(rng: () => number, min: number, maxInclusive: number): number {
  return min + Math.floor(rng() * (maxInclusive - min + 1));
}

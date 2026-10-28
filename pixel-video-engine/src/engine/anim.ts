// 시간 규칙.
// - 캐릭터·오브젝트(스프라이트, 파티클, 용암 일렁임): 4프레임마다 한 번 갱신 → animStep() 사용
// - UI 모션(카메라 팬, 막대 차오르기): 매 프레임 갱신 허용, 그리기 시 정수 스냅은 Painter가 처리

export const ANIM_STEP = 4;

/** 계단식 애니메이션의 현재 스텝 번호 (24fps 기준 초당 6회 증가) */
export function animStep(frame: number): number {
  return Math.floor(frame / ANIM_STEP);
}

/** 반복 애니메이션의 프레임 인덱스. hold = 한 그림을 몇 스텝 유지할지 */
export function loopFrame(frame: number, frameCount: number, hold = 1): number {
  return Math.floor(animStep(frame) / hold) % frameCount;
}

/**
 * 1회성 애니메이션: startFrame에 시작해서 frameCount장을 한 번 재생, 끝나면 null.
 * 스텝 경계는 전역 4프레임 그리드에 맞춘다(시작 프레임이 4의 배수가 아니어도 갱신 간격 유지).
 */
export function onceFrame(frame: number, startFrame: number, frameCount: number, hold = 1): number | null {
  const steps = animStep(frame) - animStep(startFrame);
  if (steps < 0) return null;
  const i = Math.floor(steps / hold);
  return i < frameCount ? i : null;
}

export const easing = {
  linear: (t: number) => t,
  easeOutCubic: (t: number) => 1 - Math.pow(1 - t, 3),
  easeInOutQuad: (t: number) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2),
};

export type Easing = (t: number) => number;

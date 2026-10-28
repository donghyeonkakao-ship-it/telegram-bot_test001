import { easing as E, type Easing } from './anim';
import type { PropsHistoryEntry } from './scene';

/**
 * 같은 장면 안에서 줄이 바뀔 때마다 값을 이어서 보간한다.
 * 새 줄이 시작되는 순간의 "화면에 보이던 값"에서 새 목표값으로 출발하므로,
 * 이전 보간이 끝나기 전에 줄이 바뀌어도 값이 튀지 않는다. frame만으로 결정되는 순수 함수.
 *
 * @param initial 장면 첫 줄의 출발값. 생략하면 첫 줄은 보간 없이 목표값에서 시작.
 */
export function chainTween<P>(
  history: PropsHistoryEntry<P>[],
  frame: number,
  get: (props: P) => number,
  { duration, easing = E.easeOutCubic, initial }: { duration: number; easing?: Easing; initial?: number },
): number {
  if (history.length === 0) throw new Error('chainTween: history가 비어 있음');

  const evalAt = (tw: { start: number; from: number; to: number }, f: number) => {
    const t = duration <= 0 ? 1 : Math.min(1, Math.max(0, (f - tw.start) / duration));
    return tw.from + (tw.to - tw.from) * easing(t);
  };

  const first = get(history[0].props);
  let tw = { start: history[0].startFrame, from: initial ?? first, to: first };
  for (let i = 1; i < history.length; i++) {
    const { startFrame, props } = history[i];
    if (startFrame > frame) break;
    tw = { start: startFrame, from: evalAt(tw, startFrame), to: get(props) };
  }
  return evalAt(tw, frame);
}

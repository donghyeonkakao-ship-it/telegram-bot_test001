import type { PropsHistoryEntry } from './scene';
import type { Script, ScriptLine } from './script';

// script → 장면 구간 계산.
// 같은 scene이 연속되는 줄은 하나의 구간(SceneSegment)으로 묶여 끊김 없이 이어서 재생된다.
// scene이 바뀌는 지점은 하드 컷.

export type TimedLine = ScriptLine & {
  /** 전체 영상 기준 프레임 */
  startFrame: number;
  endFrame: number;
};

export type SceneSegment = {
  sceneId: string;
  /** 전체 영상 기준 시작 프레임 */
  from: number;
  durationInFrames: number;
  /** 구간 안의 줄. startFrame/endFrame은 구간 기준 로컬 프레임 */
  lines: TimedLine[];
};

export type Timeline = {
  durationInFrames: number;
  /** 전체 기준 프레임의 줄 목록 (자막용) */
  lines: TimedLine[];
  segments: SceneSegment[];
};

export const secToFrame = (sec: number, fps: number) => Math.round(sec * fps);

export function buildTimeline(script: Script, fps: number): Timeline {
  const lines: TimedLine[] = script.lines.map((l) => ({
    ...l,
    startFrame: secToFrame(l.start, fps),
    endFrame: Math.max(secToFrame(l.end, fps), secToFrame(l.start, fps) + 1),
  }));
  const durationInFrames = Math.max(1, lines[lines.length - 1].endFrame);

  const groups: TimedLine[][] = [];
  for (const line of lines) {
    const last = groups[groups.length - 1];
    if (last && last[0].scene === line.scene) last.push(line);
    else groups.push([line]);
  }

  const segments = groups.map((group, i): SceneSegment => {
    // 첫 구간은 0프레임부터, 이후 구간은 첫 줄 시작부터 다음 구간 시작까지 (구간 사이 빈틈 없음)
    const from = i === 0 ? 0 : group[0].startFrame;
    const next = groups[i + 1];
    const to = next ? next[0].startFrame : durationInFrames;
    return {
      sceneId: group[0].scene,
      from,
      durationInFrames: Math.max(1, to - from),
      lines: group.map((l) => ({ ...l, startFrame: l.startFrame - from, endFrame: l.endFrame - from })),
    };
  });

  return { durationInFrames, lines, segments };
}

/** 구간 안 로컬 프레임에서 현재 줄과 props 이력을 구한다. 줄 사이 빈 시간에는 직전 줄이 유지된다. */
export function sceneStateAt(segment: SceneSegment, localFrame: number) {
  let current = 0;
  for (let i = 0; i < segment.lines.length; i++) {
    if (segment.lines[i].startFrame <= localFrame) current = i;
  }
  const line = segment.lines[current];
  const history: PropsHistoryEntry<unknown>[] = segment.lines.slice(0, current + 1).map((l, i) => ({
    props: l.props,
    // 장면의 첫 줄은 장면 시작(0)부터 유효
    startFrame: i === 0 ? 0 : l.startFrame,
  }));
  const lineStartFrame = history[current].startFrame;
  return {
    props: line.props,
    prevProps: current > 0 ? segment.lines[current - 1].props : null,
    lineStartFrame,
    lineFrame: localFrame - lineStartFrame,
    history,
  };
}

/** 전체 기준 프레임에서 자막으로 보일 줄 (start ≤ t < end) */
export function lineAt(timeline: Timeline, frame: number): TimedLine | null {
  return timeline.lines.find((l) => l.startFrame <= frame && frame < l.endFrame) ?? null;
}

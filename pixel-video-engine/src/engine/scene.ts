import type React from 'react';
import type { z } from 'zod';

/** 장면 안에서 한 줄(line)이 시작된 시점과 그 줄의 props */
export type PropsHistoryEntry<P> = { props: P; startFrame: number };

export type SceneProps<P> = {
  /** 현재 장면(같은 scene이 이어지는 구간) 안에서의 로컬 프레임 */
  frame: number;
  fps: number;
  /** 현재 줄의 props */
  props: P;
  /** 같은 장면 안 이전 줄의 props. 장면의 첫 줄이면 null */
  prevProps: P | null;
  /** 현재 줄이 시작된 로컬 프레임 / 현재 줄 시작 후 경과 프레임 */
  lineStartFrame: number;
  lineFrame: number;
  /** 장면 시작부터 현재 줄까지의 props 이력 (전환 보간용, chainTween과 함께 사용) */
  history: PropsHistoryEntry<P>[];
};

export type SceneDef<P = unknown> = {
  id: string;
  propsSchema: z.ZodType<P, unknown>;
  component: React.FC<SceneProps<P>>;
};

export function defineScene<S extends z.ZodType>(def: {
  id: string;
  propsSchema: S;
  component: React.FC<SceneProps<z.output<S>>>;
}): SceneDef<z.output<S>> {
  return def as SceneDef<z.output<S>>;
}

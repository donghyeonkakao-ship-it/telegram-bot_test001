import { z } from 'zod';
import type { SceneDef } from './scene';

export const lineSchema = z.object({
  text: z.string(),
  start: z.number().min(0),
  end: z.number(),
  scene: z.string().min(1),
  props: z.record(z.string(), z.unknown()).default({}),
});

export const scriptSchema = z.object({
  title: z.string(),
  lines: z.array(lineSchema).min(1),
});

export type RawScript = z.input<typeof scriptSchema>;

export type ScriptLine = {
  index: number;
  text: string;
  start: number;
  end: number;
  scene: string;
  /** 해당 장면의 propsSchema로 검증·기본값 적용이 끝난 props */
  props: unknown;
};

export type Script = { title: string; lines: ScriptLine[] };

export class ScriptError extends Error {
  constructor(message: string) {
    super(`[script.json] ${message}`);
    this.name = 'ScriptError';
  }
}

const formatZod = (err: z.ZodError) => err.issues.map((i) => `${i.path.join('.') || '(root)'}: ${i.message}`).join('; ');

/**
 * 대본을 검증한다. 렌더 전(calculateMetadata)에 호출되어 문제가 있으면 렌더를 시작하지 않는다.
 * - 구조(zod)
 * - start < end, 줄끼리 시간 겹침 없음, 시간순 정렬
 * - 등록되지 않은 scene 이름
 * - 각 줄 props를 해당 장면 propsSchema로 검증
 */
export function validateScript(raw: unknown, registry: Record<string, SceneDef<unknown>>): Script {
  const parsed = scriptSchema.safeParse(raw);
  if (!parsed.success) throw new ScriptError(formatZod(parsed.error));

  const known = Object.keys(registry);
  const lines = parsed.data.lines.map((line, index): ScriptLine => {
    const where = `lines[${index}] "${line.text}"`;
    if (!(line.end > line.start)) throw new ScriptError(`${where}: end(${line.end})는 start(${line.start})보다 커야 함`);
    const prev = parsed.data.lines[index - 1];
    if (prev && line.start < prev.end) throw new ScriptError(`${where}: 이전 줄(end ${prev.end})과 시간이 겹치거나 순서가 뒤바뀜`);

    const scene = registry[line.scene];
    if (!scene) throw new ScriptError(`${where}: 등록되지 않은 scene "${line.scene}" (등록된 장면: ${known.join(', ')})`);

    const props = scene.propsSchema.safeParse(line.props);
    if (!props.success) throw new ScriptError(`${where}: scene "${line.scene}" props 오류 — ${formatZod(props.error)}`);

    return { index, text: line.text, start: line.start, end: line.end, scene: line.scene, props: props.data };
  });

  return { title: parsed.data.title, lines };
}

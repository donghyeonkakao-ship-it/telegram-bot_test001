// npm install 후 폰트(OFL)를 node_modules에서 public/fonts로 복사한다.
import { copyFileSync, mkdirSync } from 'node:fs';

const fonts = [
  ['node_modules/pretendard/dist/web/static/woff2/Pretendard-Bold.woff2', 'public/fonts/Pretendard-Bold.woff2'],
  ['node_modules/galmuri/dist/Galmuri11.woff2', 'public/fonts/Galmuri11.woff2'],
];

mkdirSync('public/fonts', { recursive: true });
for (const [src, dst] of fonts) copyFileSync(src, dst);
console.log('fonts copied to public/fonts');

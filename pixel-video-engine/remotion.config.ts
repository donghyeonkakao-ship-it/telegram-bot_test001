import { Config } from '@remotion/cli/config';

Config.setEntryPoint('src/index.ts');
// 중간 프레임을 PNG로 받아야 픽셀 경계가 JPEG 압축으로 뭉개지지 않는다.
Config.setVideoImageFormat('png');
Config.setCodec('h264');
Config.setCrf(16);
Config.setPixelFormat('yuv420p');
Config.setOverwriteOutput(true);

import { MediaTrackItem } from '../types';

export const SAMPLE_MEDIA_PLAYLIST: MediaTrackItem[] = [
  {
    id: 'track-1',
    title: 'MEDHĀ Cyberpunk City Demo Reel',
    type: 'video',
    durationSec: 145,
    url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    artist: 'MEDHĀ Motion Studios',
    codec: 'H.264 / AAC',
    resolution: '1920x1080 (60FPS)'
  },
  {
    id: 'track-2',
    title: 'Autonomous Offline AI Soundtrack',
    type: 'audio',
    durationSec: 210,
    url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
    artist: 'MEDHĀ Audio Engine',
    codec: 'MP3 320kbps Stereo'
  },
  {
    id: 'track-3',
    title: 'Graphics & Shader Renderer Preview',
    type: 'video',
    durationSec: 98,
    url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4',
    artist: 'MEDHĀ GPU Shader Lab',
    codec: 'VP9 / Opustech',
    resolution: '3840x2160 (4K 60FPS)'
  }
];

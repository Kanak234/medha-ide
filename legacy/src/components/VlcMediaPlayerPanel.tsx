import React, { useState, useRef } from 'react';
import { Play, Pause, Volume2, VolumeX, Maximize2, SkipForward, SkipBack, Video, Music, Film, Info, Radio } from 'lucide-react';
import { SAMPLE_MEDIA_PLAYLIST } from '../services/mediaEngine';
import { MediaTrackItem } from '../types';

export const VlcMediaPlayerPanel: React.FC = () => {
  const [playlist] = useState<MediaTrackItem[]>(SAMPLE_MEDIA_PLAYLIST);
  const [activeTrackId, setActiveTrackId] = useState<string>('track-1');
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [volume, setVolume] = useState<number>(80);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1.0);
  const videoRef = useRef<HTMLVideoElement>(null);

  const activeTrack = playlist.find(t => t.id === activeTrackId) || playlist[0];

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play().catch(() => {});
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <div className="flex-1 bg-[#090d16] flex flex-col h-full overflow-hidden select-none">
      {/* Top VLC Header Bar */}
      <div className="h-11 bg-[#0f172a] border-b border-[#1e293b] flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <Film className="w-5 h-5 text-amber-500" />
          <span className="font-bold text-xs uppercase tracking-wider text-white">VLC Media Player & Asset Previewer</span>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold border border-amber-500/30">
            LibVLC 3.0.20 Embedded
          </span>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={playbackSpeed}
            onChange={(e) => {
              const speed = parseFloat(e.target.value);
              setPlaybackSpeed(speed);
              if (videoRef.current) videoRef.current.playbackRate = speed;
            }}
            className="bg-[#1e293b] border border-[#334155] text-xs font-semibold text-white rounded px-2 py-1 focus:outline-none cursor-pointer"
          >
            <option value="0.5">0.5x Speed</option>
            <option value="1.0">1.0x Speed (Normal)</option>
            <option value="1.5">1.5x Speed</option>
            <option value="2.0">2.0x Speed</option>
          </select>
        </div>
      </div>

      {/* Main Player Workspace */}
      <div className="flex-1 flex overflow-hidden">
        {/* Playlist Sidebar */}
        <div className="w-72 bg-[#0f172a] border-r border-[#1e293b] p-3 flex flex-col space-y-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 border-b border-[#1e293b] pb-2 flex items-center gap-1.5">
            <Radio className="w-4 h-4 text-amber-500" /> Media Playlist
          </span>

          <div className="flex-1 overflow-y-auto space-y-2">
            {playlist.map((track) => (
              <div
                key={track.id}
                onClick={() => {
                  setActiveTrackId(track.id);
                  setIsPlaying(false);
                }}
                className={`p-3 rounded-xl cursor-pointer text-xs border transition-all ${
                  activeTrackId === track.id
                    ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 font-semibold'
                    : 'bg-[#1e293b]/40 text-[#94a3b8] border-[#334155]/40 hover:text-white'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  {track.type === 'video' ? <Video className="w-4 h-4 text-amber-400 shrink-0" /> : <Music className="w-4 h-4 text-sky-400 shrink-0" />}
                  <span className="font-bold truncate">{track.title}</span>
                </div>
                <div className="text-[11px] text-slate-400 font-mono flex items-center justify-between">
                  <span>{track.artist}</span>
                  <span>{Math.floor(track.durationSec / 60)}:{(track.durationSec % 60).toString().padStart(2, '0')}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Video Viewport Stage */}
        <div className="flex-1 bg-[#060911] flex flex-col overflow-hidden">
          <div className="flex-1 flex items-center justify-center p-6 relative overflow-hidden">
            <div className="w-full max-w-4xl h-[420px] bg-[#000000] rounded-2xl border border-[#334155] shadow-2xl flex items-center justify-center relative overflow-hidden">
              {activeTrack.type === 'video' ? (
                <video
                  ref={videoRef}
                  src={activeTrack.url}
                  controls={false}
                  className="w-full h-full object-contain"
                />
              ) : (
                <div className="flex flex-col items-center justify-center space-y-4">
                  <div className="w-24 h-24 rounded-full bg-amber-500/20 border border-amber-500/40 flex items-center justify-center animate-pulse">
                    <Music className="w-12 h-12 text-amber-400" />
                  </div>
                  <span className="text-sm font-bold text-white">{activeTrack.title}</span>
                </div>
              )}
            </div>
          </div>

          {/* Bottom Player Controls Strip */}
          <div className="h-16 bg-[#0f172a] border-t border-[#1e293b] px-6 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={togglePlay}
                className="w-10 h-10 rounded-full bg-amber-500 hover:bg-amber-400 text-black flex items-center justify-center transition-all shadow-lg font-bold"
              >
                {isPlaying ? <Pause className="w-5 h-5 fill-current" /> : <Play className="w-5 h-5 fill-current ml-0.5" />}
              </button>

              <div>
                <div className="text-xs font-bold text-white">{activeTrack.title}</div>
                <div className="text-[11px] text-slate-400 font-mono">{activeTrack.codec} | {activeTrack.resolution || 'Stereo Audio'}</div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Volume2 className="w-4 h-4 text-slate-400" />
              <input
                type="range"
                min="0"
                max="100"
                value={volume}
                onChange={(e) => setVolume(parseInt(e.target.value))}
                className="w-24 accent-amber-500 cursor-pointer"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

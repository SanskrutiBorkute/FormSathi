import React, { useRef, useState, useEffect } from 'react';
import { Camera, X, RefreshCw } from 'lucide-react';

export default function CameraCapture({ onCapture, onClose }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    async function startCamera() {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }
        });
        videoRef.current.srcObject = mediaStream;
        setStream(mediaStream);
      } catch (err) {
        setError('Camera permission denied or camera not found. Try uploading a photo instead.');
        console.error(err);
      }
    }
    startCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const handleCapture = () => {
    if (canvasRef.current && videoRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const dataUrl = canvas.toDataURL('image/png');
      onCapture(dataUrl);
    }
  };

  return (
    <div className="fixed inset-0 bg-ink bg-opacity-80 z-[1000] flex items-center justify-center p-4">
      <div className="bg-paper rounded-xl w-full max-w-xl overflow-hidden shadow-lg border border-paper-darker flex flex-col">
        <div className="bg-teal text-white p-4 flex justify-between items-center">
          <h3 className="font-serif font-bold text-lg flex items-center gap-2">
            <Camera className="w-5 h-5 text-saffron" /> Camera Form Scan
          </h3>
          <button onClick={onClose} className="p-1 rounded-full hover:bg-teal-dark transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="relative aspect-video bg-black flex items-center justify-center">
          {error ? (
            <p className="text-red-light font-medium p-6 text-center text-sm">{error}</p>
          ) : (
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full h-full object-cover"
            />
          )}
          <canvas ref={canvasRef} className="hidden" />
        </div>

        <div className="p-4 bg-paper-dark flex justify-center gap-4">
          {!error && (
            <button
              onClick={handleCapture}
              className="bg-teal text-white px-6 py-2.5 rounded-lg font-bold hover:bg-teal-dark transition-all flex items-center gap-2 shadow-sm"
            >
              <Camera className="w-5 h-5" /> Capture Form
            </button>
          )}
          <button
            onClick={onClose}
            className="border border-ink-light px-5 py-2.5 rounded-lg font-bold hover:bg-paper-darker transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

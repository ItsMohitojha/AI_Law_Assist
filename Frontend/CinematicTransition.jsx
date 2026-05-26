import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, useAnimation } from 'framer-motion';

// --- Spring Presets ---
const snipSpring = { type: 'spring', stiffness: 400, damping: 30 };
const smoothSpring = { type: 'spring', stiffness: 200, damping: 20 };
const elasticSpring = { type: 'spring', stiffness: 120, damping: 14 };

// --- Typing Phrases ---
const ROTATING_PHRASES = [
  "Law at work.",
  "Ask away.",
  "Your legal AI assistant.",
  "Grounded in Indian law.",
  "Ask Nyaya anything."
];

// --- Custom Canvas Particles Component (High-Performance Background) ---
const ParticleBackground = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const particles = [];
    const particleCount = 45;

    class Particle {
      constructor() {
        this.reset();
      }

      reset() {
        this.x = Math.random() * width;
        this.y = height + Math.random() * 100;
        this.size = Math.random() * 2 + 0.8;
        this.speedY = Math.random() * 0.4 + 0.2;
        this.speedX = Math.random() * 0.2 - 0.1;
        this.alpha = Math.random() * 0.5 + 0.1;
        this.angle = Math.random() * Math.PI * 2;
        this.spinSpeed = Math.random() * 0.02 - 0.01;
      }

      update() {
        this.y -= this.speedY;
        this.angle += this.spinSpeed;
        this.x += Math.sin(this.angle) * 0.15 + this.speedX;

        // Fade out as it rises near the top
        if (this.y < height * 0.1) {
          this.alpha -= 0.005;
        }

        if (this.y < 0 || this.alpha <= 0) {
          this.reset();
        }
      }

      draw() {
        ctx.save();
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        // Soft golden glow
        ctx.fillStyle = `rgba(218, 165, 32, ${this.alpha})`;
        ctx.shadowColor = 'rgba(218, 165, 32, 0.4)';
        ctx.shadowBlur = 4;
        ctx.fill();
        ctx.restore();
      }
    }

    // Initialize particles
    for (let i = 0; i < particleCount; i++) {
      const p = new Particle();
      p.y = Math.random() * height; // Distribute across screen initially
      particles.push(p);
    }

    const handleResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    const animate = () => {
      ctx.clearRect(0, 0, width, height);
      particles.forEach((p) => {
        p.update();
        p.draw();
      });
      animationFrameId = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return <canvas ref={canvasRef} className="absolute inset-0 w-full h-full pointer-events-none z-0" />;
};

// --- Main Cinematic Transition Component ---
export default function CinematicTransition({ onTransitionComplete }) {
  // States: 'idle' -> 'cursor-arriving' -> 'hovered' -> 'clicking' -> 'morphing' -> 'completed'
  const [timelineState, setTimelineState] = useState('idle');
  const [typedText, setTypedText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [phraseIndex, setPhraseIndex] = useState(0);
  const [rippleActive, setRippleActive] = useState(false);
  const [buttonCompressed, setButtonCompressed] = useState(false);

  const containerRef = useRef(null);

  const handleClick = () => {
    if (timelineState !== 'idle') return;
    setRippleActive(true);
    setButtonCompressed(true);
    setTimelineState('clicking');
  };

  // Handle steps based on timeline state transitions
  useEffect(() => {
    if (timelineState === 'clicking') {
      // Decompress button and proceed to Step 4: Morph
      const morphTimer = setTimeout(() => {
        setButtonCompressed(false);
        setTimelineState('morphing');
      }, 300);
      return () => clearTimeout(morphTimer);
    }

    if (timelineState === 'morphing') {
      // Wait for morph movement to finish then proceed to active chat input textbox
      const finishTimer = setTimeout(() => {
        setTimelineState('completed');
        if (onTransitionComplete) {
          // Let parent route know the transition is ready (with a slight delay)
          setTimeout(onTransitionComplete, 4000);
        }
      }, 1400);
      return () => clearTimeout(finishTimer);
    }
  }, [timelineState]);

  // 2. Typewriter Loop (triggers in 'completed' state)
  useEffect(() => {
    if (timelineState !== 'completed') return;

    let timer;
    const currentPhrase = ROTATING_PHRASES[phraseIndex];

    if (isDeleting) {
      // Deleting animation
      timer = setTimeout(() => {
        setTypedText(currentPhrase.substring(0, typedText.length - 1));
      }, 50 + Math.random() * 30); // Realistic deleting speed
    } else {
      // Typing animation
      timer = setTimeout(() => {
        setTypedText(currentPhrase.substring(0, typedText.length + 1));
      }, 90 + Math.random() * 60); // Variable typing speed
    }

    // Determine state changes
    if (!isDeleting && typedText === currentPhrase) {
      // Pause at full word
      timer = setTimeout(() => setIsDeleting(true), 1500);
    } else if (isDeleting && typedText === '') {
      setIsDeleting(false);
      setPhraseIndex((prev) => (prev + 1) % ROTATING_PHRASES.length);
    }

    return () => clearTimeout(timer);
  }, [typedText, isDeleting, phraseIndex, timelineState]);

  // Responsive animation values for Logo Wrapper
  const logoAnimate = {
    left: (timelineState === 'morphing' || timelineState === 'completed') ? '-6px' : '50%',
    x: (timelineState === 'morphing' || timelineState === 'completed') ? '0%' : '-50%',
    y: '-50%',
    scale: (timelineState === 'morphing' || timelineState === 'completed')
      ? 0.45
      : buttonCompressed
      ? 0.93
      : timelineState === 'hovered'
      ? 1.06
      : 1
  };

  const logoTransition = {
    duration: 1.3,
    ease: [0.19, 1, 0.22, 1]
  };

  return (
    <div
      ref={containerRef}
      className="relative flex flex-col items-center justify-center w-full h-screen overflow-hidden bg-[#0c0c14] select-none z-10"
    >
      {/* ── Background Particles & Lighting ── */}
      <ParticleBackground />

      <div className="absolute top-1/4 left-1/4 w-[35vw] h-[35vh] rounded-full bg-[radial-gradient(circle,rgba(218,165,32,0.06)_0%,rgba(0,0,0,0)_70%)] blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[45vw] h-[45vh] rounded-full bg-[radial-gradient(circle,rgba(65,161,207,0.08)_0%,rgba(0,0,0,0)_70%)] blur-3xl pointer-events-none" />

      {/* ── CENTRAL STAGE / TEXTBOX DOCK ── */}
      <div className="relative flex items-center justify-center w-full max-w-4xl h-48 px-6">
        
        {/* Step 4 & 5: Inner elements layout */}
        <div className="relative flex items-center justify-center w-full">
          
          {/* Logo Button & Container */}
          <motion.div
            initial={{ left: '50%', x: '-50%', y: '-50%', scale: 1 }}
            animate={logoAnimate}
            transition={logoTransition}
            className="absolute z-30 top-1/2"
          >
            <motion.button
              whileHover={timelineState === 'idle' ? {
                scale: 1.06,
                boxShadow: '0 0 35px rgba(218, 165, 32, 0.4), inset 0 0 20px rgba(255,255,255,0.06)'
              } : undefined}
              whileTap={timelineState === 'idle' ? { scale: 0.93 } : undefined}
              animate={{
                scale: buttonCompressed ? 0.93 : 1,
                boxShadow: (timelineState === 'morphing' || timelineState === 'completed')
                  ? '0 5px 15px rgba(0,0,0,0.4)'
                  : '0 10px 30px rgba(0,0,0,0.5), inset 0 0 10px rgba(255,255,255,0.03)'
              }}
              transition={{
                scale: { duration: 0.1 },
                boxShadow: { duration: 0.3 }
              }}
              onClick={handleClick}
              className="relative w-28 h-28 rounded-full bg-gradient-to-br from-[#1b1b26] to-[#0c0c14] border border-[rgba(218,165,32,0.3)] backdrop-blur-md flex items-center justify-center group overflow-hidden"
              aria-label="Enter Nyaya"
            >
              {/* Inner Glass Shimmer Effect */}
              <div className="absolute inset-0 bg-[linear-gradient(120deg,transparent_25%,rgba(255,255,255,0.05)_40%,rgba(255,255,255,0.08)_50%,rgba(255,255,255,0.05)_60%,transparent_75%)] -translate-x-[200%] group-hover:translate-x-[200%] transition-transform duration-1000 ease-out" />
              
              {/* Scales of Justice Icon */}
              <svg className="w-12 h-12 text-[#e5c158]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 3v18M3 7l9-4 9 4M5.5 7l-2 7c0 1.7 1.7 3 3.5 3s3.5-1.3 3.5-3l-2-7M15.5 7l-2 7c0 1.7 1.7 3 3.5 3s3.5-1.3 3.5-3l-2-7M8 21h8" />
              </svg>

              {/* Click Ripple Wave (Absolute element) */}
              <AnimatePresence>
                {rippleActive && (
                  <motion.span
                    initial={{ scale: 0.3, opacity: 0.8 }}
                    animate={{ scale: 2.2, opacity: 0 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.6, ease: 'easeOut' }}
                    onAnimationComplete={() => setRippleActive(false)}
                    className="absolute inset-0 rounded-full border border-[#e5c158] pointer-events-none"
                  />
                )}
              </AnimatePresence>
            </motion.button>
          </motion.div>

          {/* Step 5: Glassmorphism Textbox Emergence */}
          <AnimatePresence>
            {(timelineState === 'morphing' || timelineState === 'completed') && (
              <motion.div
                initial={{ width: '80px', opacity: 0 }}
                animate={{ width: '100%', opacity: 1 }}
                transition={{ duration: 1.1, ease: [0.19, 1, 0.22, 1], delay: 0.2 }}
                className="relative h-20 bg-gradient-to-r from-[#171722]/80 to-[#12121a]/85 border border-[rgba(218,165,32,0.18)] rounded-full backdrop-blur-xl shadow-[0_20px_50px_rgba(0,0,0,0.6)] flex items-center pl-28 pr-8"
              >
                {/* Gold Edge Highlight Glow */}
                <div className="absolute inset-0 rounded-full border border-t-[rgba(218,165,32,0.15)] border-b-transparent pointer-events-none" />

                {/* Simulated AI Text Area */}
                <div className="flex items-center w-full font-sans text-lg text-white/90 font-light select-none">
                  <span>{typedText}</span>
                  <motion.span
                    animate={{ opacity: [1, 0, 1] }}
                    transition={{ repeat: Infinity, duration: 0.8, ease: 'easeInOut' }}
                    className="ml-1 w-[2px] h-5 bg-[#e5c158]"
                  />
                </div>

                {/* Simulated Send Button */}
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.8, duration: 0.3 }}
                  className="w-11 h-11 bg-[#0081c0] rounded-full flex items-center justify-center text-white shadow-[0_4px_12px_rgba(0,129,192,0.3)] ml-auto cursor-pointer"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="22" y1="2" x2="11" y2="13" />
                    <polygon points="22 2 15 22 11 13 2 9 22 2" />
                  </svg>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* ── Subtitle Copy (Only visible during Step 1 & 2) ── */}
      <AnimatePresence>
        {timelineState !== 'morphing' && timelineState !== 'completed' && (
          <motion.div
            initial={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 15 }}
            transition={{ duration: 0.4 }}
            className="absolute bottom-[32vh] flex flex-col items-center gap-2"
          >
            <h2 className="font-serif text-[#fefffc] text-xl font-light tracking-[0.15em] uppercase">
              Enter Nyaya
            </h2>
            <p className="font-sans text-xs text-white/40 tracking-[0.08em] uppercase">
              Click the scales of justice to unlock RAG Legal AI
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Cinematic Ambient Shadow Ring ── */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_40%,rgba(6,6,10,0.95)_100%)] pointer-events-none z-1" />
    </div>
  );
}

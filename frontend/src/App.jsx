import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FileText, Camera, ShieldAlert, CheckCircle, AlertTriangle, Play, Volume2,
  User, LayoutDashboard, LogOut, ArrowLeft, RefreshCw, Upload, Plus, HelpCircle, FileCheck
} from 'lucide-react';
import { 
  ResponsiveContainer, LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend 
} from 'recharts';
import CameraCapture from './components/CameraCapture';
import SmartAssistant from './components/SmartAssistant';

// Configure Axios defaults
axios.defaults.baseURL = 'http://127.0.0.1:5000';

const highContrastStyles = `
  .high-contrast {
    background-color: #000000 !important;
    color: #FFFFFF !important;
  }
  .high-contrast .bg-white,
  .high-contrast .bg-paper,
  .high-contrast .bg-paper-dark,
  .high-contrast .bg-teal,
  .high-contrast .bg-teal-dark {
    background-color: #121212 !important;
    color: #FFFFFF !important;
    border-color: #FFFFFF !important;
  }
  .high-contrast text,
  .high-contrast span,
  .high-contrast p,
  .high-contrast h1,
  .high-contrast h2,
  .high-contrast h3,
  .high-contrast h4,
  .high-contrast h5,
  .high-contrast h6,
  .high-contrast label,
  .high-contrast input {
    color: #FFFF00 !important;
  }
  .high-contrast border,
  .high-contrast .border,
  .high-contrast .border-paper-darker {
    border: 2px solid #FFFFFF !important;
  }
  .high-contrast button {
    background-color: #FFFF00 !important;
    color: #000000 !important;
    border: 2px solid #FFFFFF !important;
    font-weight: 900 !important;
  }
`;

// Helper components for UI Showcase Polish
function CompletenessRing({ completed, total, compact }) {
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
  
  let rating = "Incomplete";
  let colorClass = "text-red";
  let bgStroke = "#FDECEA";
  let strokeColor = "#C0392B";
  
  if (percentage >= 90) {
    rating = "Excellent";
    colorClass = "text-green";
    bgStroke = "#EBF7EE";
    strokeColor = "#1E7B3A";
  } else if (percentage >= 70) {
    rating = "Good";
    colorClass = "text-teal";
    bgStroke = "#E3F2F3";
    strokeColor = "#0D5C63";
  } else if (percentage >= 50) {
    rating = "Needs Attention";
    colorClass = "text-saffron-dark";
    bgStroke = "#FEF5E7";
    strokeColor = "#F4A024";
  }
  
  const radius = 24;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;
  
  if (compact) {
    return (
      <div className="flex items-center gap-2.5 text-white">
        <div className="relative w-12 h-12 flex-shrink-0">
          <svg className="w-full h-full transform -rotate-90">
            <circle cx="24" cy="24" r={radius} stroke="rgba(255,255,255,0.15)" strokeWidth="4" fill="transparent" />
            <circle cx="24" cy="24" r={radius} stroke="#F4A024" strokeWidth="4" fill="transparent" strokeDasharray={circumference} strokeDashoffset={strokeDashoffset} strokeLinecap="round" />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center font-mono font-bold text-[10px]">
            {percentage}%
          </div>
        </div>
        <div className="text-left">
          <div className="text-[8px] text-teal-light font-bold uppercase tracking-wider">Completeness</div>
          <div className="text-[10px] font-black text-saffron">{rating}</div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="flex items-center gap-3 bg-white border border-paper-darker rounded-xl p-3 shadow-sm-custom w-full">
      <div className="relative w-14 h-14 flex-shrink-0">
        <svg className="w-full h-full transform -rotate-90">
          <circle cx="28" cy="28" r="22" stroke={bgStroke} strokeWidth="4" fill="transparent" />
          <circle cx="28" cy="28" r="22" stroke={strokeColor} strokeWidth="4" fill="transparent" strokeDasharray={2 * Math.PI * 22} strokeDashoffset={2 * Math.PI * 22 - (percentage / 100) * (2 * Math.PI * 22)} strokeLinecap="round" className="transition-all duration-500 ease-out" />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center font-mono font-bold text-xs text-ink">
          {percentage}%
        </div>
      </div>
      <div className="min-w-0 flex-1">
        <div className="text-[9px] text-ink-light font-bold uppercase tracking-wider">Completeness</div>
        <div className={`text-xs font-black truncate ${colorClass}`}>{rating}</div>
        <div className="text-[9px] text-ink-medium font-semibold truncate">{completed}/{total} inputs valid</div>
      </div>
    </div>
  );
}

function getConfidenceBadge(confidence) {
  const pct = Math.round(confidence * 100);
  if (pct >= 90) {
    return (
      <span className="text-[9px] font-black px-2 py-0.5 rounded-full bg-green-light text-green border border-green/20 flex items-center gap-1">
        <span className="w-1 h-1 rounded-full bg-green"></span> OCR: {pct}%
      </span>
    );
  }
  if (pct >= 70) {
    return (
      <span className="text-[9px] font-black px-2 py-0.5 rounded-full bg-saffron-light text-saffron-dark border border-saffron/20 flex items-center gap-1">
        <span className="w-1 h-1 rounded-full bg-saffron"></span> OCR: {pct}%
      </span>
    );
  }
  return (
    <span className="text-[9px] font-black px-2 py-0.5 rounded-full bg-red-light text-red border border-red/20 flex items-center gap-1 animate-pulse">
      <span className="w-1 h-1 rounded-full bg-red"></span> OCR: {pct}%
    </span>
  );
}

// Side-by-side comparison modal/view
function CompareModal({ forms, onClose, showToast }) {
  const [formA, setFormA] = useState(null);
  const [formB, setFormB] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function fetchForms() {
      try {
        const token = localStorage.getItem('token');
        const [resA, resB] = await Promise.all([
          axios.get(`/api/forms/${forms[0].id}`, { headers: { Authorization: `Bearer ${token}` } }),
          axios.get(`/api/forms/${forms[1].id}`, { headers: { Authorization: `Bearer ${token}` } })
        ]);
        setFormA(resA.data);
        setFormB(resB.data);
      } catch (err) {
        console.error(err);
        showToast("Error loading forms comparison details.", "error");
      } finally {
        setLoading(false);
      }
    }
    fetchForms();
  }, [forms]);
  
  if (loading) {
    return (
      <div className="fixed inset-0 bg-ink/40 backdrop-blur-sm z-[999] flex items-center justify-center">
        <div className="bg-white p-6 rounded-2xl shadow-lg-custom flex items-center gap-3">
          <RefreshCw className="w-5 h-5 text-teal animate-spin" />
          <span className="text-xs font-bold text-ink">Loading comparison details...</span>
        </div>
      </div>
    );
  }
  
  // Find all distinct field labels from both forms
  const allLabels = Array.from(new Set([
    ...formA.fields.map(f => f.label),
    ...formB.fields.map(f => f.label)
  ]));
  
  return (
    <div className="fixed inset-0 bg-ink/40 backdrop-blur-sm z-[999] flex items-center justify-center p-4">
      <div className="bg-white border border-paper-darker rounded-2xl w-full max-w-4xl max-h-[85vh] flex flex-col overflow-hidden shadow-lg-custom">
        <div className="bg-teal text-white p-4 flex justify-between items-center">
          <h3 className="font-serif font-black text-sm">⚖️ Side-by-Side Form Comparison</h3>
          <button onClick={onClose} className="text-xs bg-teal-dark hover:bg-teal-medium px-2.5 py-1 rounded font-bold transition-all">Close</button>
        </div>
        
        <div className="p-4 grid grid-cols-2 gap-4 bg-paper-dark border-b border-paper-darker text-xs font-bold">
          <div>
            <h4 className="font-serif text-teal text-sm">{formA.filename}</h4>
            <span className="text-[10px] text-ink-light uppercase tracking-wider">{formA.form_type}</span>
          </div>
          <div>
            <h4 className="font-serif text-teal text-sm">{formB.filename}</h4>
            <span className="text-[10px] text-ink-light uppercase tracking-wider">{formB.form_type}</span>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4">
          <table className="w-full text-xs text-left border-collapse">
            <thead>
              <tr className="border-b border-paper-darker text-ink-light font-bold">
                <th className="py-2 w-1/3">Field Name</th>
                <th className="py-2 w-1/3">{formA.filename.slice(0, 15)}...</th>
                <th className="py-2 w-1/3">{formB.filename.slice(0, 15)}...</th>
              </tr>
            </thead>
            <tbody>
              {allLabels.map((lbl, idx) => {
                const fA = formA.fields.find(f => f.label === lbl);
                const fB = formB.fields.find(f => f.label === lbl);
                
                const valA = fA ? fA.current_value : '[N/A]';
                const valB = fB ? fB.current_value : '[N/A]';
                
                const isMismatch = valA !== valB;
                const statusA = fA ? fA.status : 'n/a';
                const statusB = fB ? fB.status : 'n/a';
                
                return (
                  <tr 
                    key={idx} 
                    className={`border-b border-paper-light hover:bg-paper/20 transition-all ${
                      isMismatch ? 'bg-saffron-light/35 font-bold' : ''
                    }`}
                  >
                    <td className="py-2.5 flex items-center gap-1.5 text-ink-medium">
                      {isMismatch && <span className="text-saffron-dark text-[10px]" title="Field value mismatch">⚠️</span>}
                      {lbl}
                    </td>
                    <td className="py-2.5">
                      <span className={`block ${statusA === 'error' ? 'text-red' : ''}`}>
                        {valA}
                      </span>
                      {fA && fA.ocr_confidence !== undefined && (
                        <span className="text-[8px] text-ink-light font-mono block">OCR: {Math.round(fA.ocr_confidence * 100)}%</span>
                      )}
                    </td>
                    <td className="py-2.5">
                      <span className={`block ${statusB === 'error' ? 'text-red' : ''}`}>
                        {valB}
                      </span>
                      {fB && fB.ocr_confidence !== undefined && (
                        <span className="text-[8px] text-ink-light font-mono block">OCR: {Math.round(fB.ocr_confidence * 100)}%</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// Floating Accessibility Control Widget
function AccessibilityWidget({ accessibility, setAccessibility }) {
  const [open, setOpen] = useState(false);
  
  const toggleContrast = () => {
    const newVal = !accessibility.highContrast;
    setAccessibility(prev => ({ ...prev, highContrast: newVal }));
    localStorage.setItem('highContrast', newVal ? 'true' : 'false');
  };
  
  const setSize = (size) => {
    setAccessibility(prev => ({ ...prev, fontSize: size }));
    localStorage.setItem('fontSize', size);
  };
  
  return (
    <div className="fixed bottom-4 left-4 z-[999] font-sans">
      <button 
        onClick={() => setOpen(!open)}
        className="w-10 h-10 bg-teal text-white rounded-full flex items-center justify-center shadow-lg hover:bg-teal-dark transition-all border border-teal-medium"
        title="Accessibility Tools"
      >
        ♿
      </button>
      
      {open && (
        <div className="absolute bottom-12 left-0 bg-white border border-paper-darker rounded-xl p-4 shadow-custom w-56 flex flex-col gap-3">
          <h4 className="font-serif font-black text-xs text-ink border-b border-paper-darker pb-1.5">Accessibility Controls</h4>
          
          <div className="flex flex-col gap-1.5">
            <span className="text-[10px] font-bold text-ink-light uppercase">Contrast Mode</span>
            <button 
              onClick={toggleContrast}
              className={`text-xs py-1.5 px-3 rounded-lg font-bold transition-all border ${
                accessibility.highContrast 
                  ? 'bg-ink text-white border-ink' 
                  : 'bg-paper text-ink border-paper-darker hover:bg-paper-dark'
              }`}
            >
              {accessibility.highContrast ? 'High Contrast: ON' : 'High Contrast: OFF'}
            </button>
          </div>
          
          <div className="flex flex-col gap-1.5">
            <span className="text-[10px] font-bold text-ink-light uppercase">Font Scaling</span>
            <div className="flex gap-1">
              {['medium', 'large', 'xlarge'].map((size) => (
                <button
                  key={size}
                  onClick={() => setSize(size)}
                  className={`text-[10px] flex-1 py-1 rounded font-bold capitalize transition-all border ${
                    accessibility.fontSize === size 
                      ? 'bg-teal text-white border-teal' 
                      : 'bg-paper text-ink border-paper-darker hover:bg-paper-dark'
                  }`}
                >
                  {size === 'medium' ? 'Norm' : size === 'large' ? 'Lg' : 'XL'}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Global Header Component
function Header({ user, onLogout, lang, setLang, demoMode, setDemoMode, showToast }) {
  const navigate = useNavigate();

  const handleLangChange = (selectedLang) => {
    setLang(selectedLang);
    localStorage.setItem('lang', selectedLang);
  };

  return (
    <nav className="bg-teal text-white px-6 md:px-10 h-16 flex items-center justify-between sticky top-0 z-50 shadow-md">
      <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
        <div className="font-serif text-2xl font-black tracking-tight">
          Form<span className="text-saffron">Saathi</span>
        </div>
        <div className="w-1.5 h-1.5 bg-saffron rounded-full self-end mb-2"></div>
      </div>

      <div className="flex items-center gap-6">
        {user && (
          <div className="hidden md:flex gap-4">
            <Link to="/" className="text-sm font-semibold hover:text-paper-dark transition-colors flex items-center gap-1.5">
              🏠 Home
            </Link>
            <Link to="/dashboard" className="text-sm font-semibold hover:text-paper-dark transition-colors flex items-center gap-1.5">
              📊 History & Analytics
            </Link>
          </div>
        )}

        <div className="flex items-center gap-4">
          {user && (
            <div className="flex items-center bg-teal-dark px-3 py-1 rounded-full border border-teal-medium">
              <label className="text-[10px] font-black uppercase text-teal-light flex items-center gap-1.5 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={demoMode}
                  onChange={(e) => {
                    const checked = e.target.checked;
                    setDemoMode(checked);
                    localStorage.setItem('demoMode', checked ? 'true' : 'false');
                    showToast(checked ? 'Demo Mode activated! Templates enabled.' : 'Demo Mode deactivated.', 'info');
                  }}
                  className="accent-saffron cursor-pointer w-3.5 h-3.5"
                />
                Demo Mode
              </label>
            </div>
          )}

          <div className="bg-teal-dark border border-teal-medium rounded-full p-0.5 flex">
            {['en', 'hi', 'mr'].map((l) => (
              <button
                key={l}
                onClick={() => handleLangChange(l)}
                className={`text-xs px-3 py-1 rounded-full font-bold uppercase transition-all ${lang === l ? 'bg-saffron text-white shadow-sm' : 'text-teal-light hover:text-white'
                  }`}
              >
                {l === 'en' ? 'EN' : l === 'hi' ? 'हि' : 'म'}
              </button>
            ))}
          </div>

          {user ? (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 bg-teal-dark px-3 py-1.5 rounded-full border border-teal-medium">
                <div className="w-6 h-6 rounded-full bg-saffron text-teal font-black text-xs flex items-center justify-center">
                  {user.name.slice(0, 2).toUpperCase()}
                </div>
                <span className="text-xs font-semibold max-w-[80px] truncate">{user.name}</span>
              </div>
              <button onClick={onLogout} className="p-2 rounded-full hover:bg-teal-dark transition-colors" title="Logout">
                <LogOut className="w-4 h-4 text-paper-dark" />
              </button>
            </div>
          ) : (
            <Link to="/login" className="bg-saffron text-white text-xs font-bold px-4 py-2 rounded-lg hover:bg-saffron-dark transition-all">
              Login
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}

// Login Component
function Login({ setUser }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await axios.post('/api/auth/login', { email, password });
      localStorage.setItem('token', response.data.token);
      setUser(response.data.user);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.message || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center p-6">
      <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="bg-white border border-paper-darker rounded-2xl p-8 shadow-custom w-full max-w-md">
        <h2 className="font-serif font-black text-2xl text-ink text-center mb-1">Welcome back</h2>
        <p className="text-center text-ink-light text-sm mb-6">Enter details to sign in to FormSaathi</p>

        {error && <div className="bg-red-light border border-red text-red text-xs p-3 rounded-lg mb-4 font-semibold">{error}</div>}

        <form onSubmit={handleLogin} className="flex flex-col gap-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-ink-medium mb-1.5">Email address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2.5 bg-paper rounded-lg border border-paper-darker focus:border-teal outline-none text-sm font-sans"
              placeholder="e.g. student@gmail.com"
            />
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-ink-medium mb-1.5">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 bg-paper rounded-lg border border-paper-darker focus:border-teal outline-none text-sm font-sans"
              placeholder="••••••••"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="bg-teal text-white py-3 rounded-lg font-bold text-sm hover:bg-teal-dark transition-all disabled:opacity-50 mt-2"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <p className="text-xs text-ink-light text-center mt-6">
          Don't have an account?{' '}
          <Link to="/register" className="text-teal font-bold hover:underline">
            Register here
          </Link>
        </p>
      </motion.div>
    </div>
  );
}

// Register Component
function Register({ setUser }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await axios.post('/api/auth/register', { name, email, password });
      localStorage.setItem('token', response.data.token);
      setUser(response.data.user);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center p-6">
      <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="bg-white border border-paper-darker rounded-2xl p-8 shadow-custom w-full max-w-md">
        <h2 className="font-serif font-black text-2xl text-ink text-center mb-1">Create Account</h2>
        <p className="text-center text-ink-light text-sm mb-6">Register to translate & validate your physical forms</p>

        {error && <div className="bg-red-light border border-red text-red text-xs p-3 rounded-lg mb-4 font-semibold">{error}</div>}

        <form onSubmit={handleRegister} className="flex flex-col gap-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-ink-medium mb-1.5">Your Name</label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2.5 bg-paper rounded-lg border border-paper-darker focus:border-teal outline-none text-sm font-sans"
              placeholder="e.g. Rahul Sharma"
            />
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-ink-medium mb-1.5">Email address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2.5 bg-paper rounded-lg border border-paper-darker focus:border-teal outline-none text-sm font-sans"
              placeholder="e.g. rahul@example.com"
            />
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-ink-medium mb-1.5">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 bg-paper rounded-lg border border-paper-darker focus:border-teal outline-none text-sm font-sans"
              placeholder="••••••••"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="bg-teal text-white py-3 rounded-lg font-bold text-sm hover:bg-teal-dark transition-all disabled:opacity-50 mt-2"
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>
        <p className="text-xs text-ink-light text-center mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-teal font-bold hover:underline">
            Login here
          </Link>
        </p>
      </motion.div>
    </div>
  );
}

// Upload/Home View
function UploadHome({ lang, demoMode, showToast }) {
  const [cameraActive, setCameraActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchBriefAnalytics() {
      try {
        const token = localStorage.getItem('token');
        const res = await axios.get('/api/analytics', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setAnalytics(res.data);
      } catch (err) {
        console.error(err);
      }
    }
    fetchBriefAnalytics();
  }, []);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`/api/forms/upload?lang=${lang}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`
        }
      });
      showToast("Form uploaded and analyzed successfully!", "success");
      navigate(`/analyze/${response.data.form_id}`);
    } catch (err) {
      showToast(err.response?.data?.message || 'Error occurred during form upload.', "error");
    } finally {
      setLoading(false);
    }
  };

  const handleCameraCapture = async (base64Image) => {
    setCameraActive(false);
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`/api/forms/camera-capture?lang=${lang}`, {
        image_data: base64Image
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      showToast("Camera capture processed and analyzed!", "success");
      navigate(`/analyze/${response.data.form_id}`);
    } catch (err) {
      showToast(err.response?.data?.message || 'Error processing camera capture.', "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pb-16">
      {/* Hero Header */}
      <div className="bg-teal-dark text-white py-16 px-6 text-center relative overflow-hidden ruled-watermark">
        <span className="inline-flex items-center gap-1.5 bg-saffron/20 border border-saffron/40 px-3.5 py-1 rounded-full text-[10px] font-bold tracking-wider uppercase text-saffron mb-4">
          🌐 Universal Form Intelligence Platform
        </span>
        <h1 className="font-serif font-black text-4xl md:text-5xl leading-tight tracking-tight mb-4">
          Read, Understand, and Fill <br /><em className="text-saffron not-italic">any form</em> in your language.
        </h1>
        <p className="max-w-xl mx-auto text-sm text-teal-light leading-relaxed mb-8">
          Upload a photo, scan, or PDF of any form (personal, business, financial, legal, or healthcare). We extract fields, calculate scores, and translate explanations dynamically.
        </p>

        {/* Upload Container */}
        <div className="bg-paper text-ink rounded-2xl w-full max-w-xl mx-auto shadow-lg-custom overflow-hidden">
          {loading ? (
            <div className="py-20 px-8 flex flex-col items-center justify-center gap-4">
              <RefreshCw className="w-10 h-10 text-teal animate-spin" />
              <h3 className="font-serif font-bold text-lg text-ink">Analyzing Form & OCR Extraction...</h3>
              <p className="text-xs text-ink-light max-w-xs text-center">Processing layout contours, reading multilingual languages (Hindi, Marathi, English) and setting up fields.</p>
            </div>
          ) : (
            <>
              <div className="p-8 border-2 border-dashed border-paper-darker rounded-xl m-4 hover:border-teal-medium hover:bg-teal-light/20 transition-all cursor-pointer flex flex-col items-center relative group">
                <input
                  type="file"
                  onChange={handleFileUpload}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                  accept=".pdf,.png,.jpg,.jpeg"
                />
                <Upload className="w-12 h-12 text-ink-light mb-4 group-hover:text-teal transition-colors" />
                <h3 className="font-serif font-bold text-lg text-ink mb-1">Drop your form document here</h3>
                <p className="text-xs text-ink-light mb-4 max-w-xs text-center">Upload any PDF, photo scan, or screenshot from your device.</p>
                <button className="bg-teal hover:bg-teal-dark text-white text-xs font-bold px-6 py-2.5 rounded-lg flex items-center gap-2 shadow-sm">
                  Upload file
                </button>
              </div>

              <div className="bg-paper-dark border-t border-paper-darker flex">
                <button
                  onClick={() => setCameraActive(true)}
                  className="flex-1 py-4 text-xs font-bold text-ink-medium hover:bg-paper-darker border-r border-paper-darker flex items-center justify-center gap-2 transition-colors"
                >
                  <Camera className="w-4 h-4 text-teal" /> Use Camera Scan
                </button>
                <Link
                  to="/dashboard"
                  className="flex-1 py-4 text-xs font-bold text-ink-medium hover:bg-paper-darker flex items-center justify-center gap-2 transition-colors"
                >
                  <LayoutDashboard className="w-4 h-4 text-saffron" /> View History Dashboard
                </Link>
              </div>
            </>
          )}
        </div>

        {/* Demo Mode Preloaded Template Switcher */}
        {demoMode && !loading && (
          <div className="max-w-xl mx-auto mt-6 bg-saffron-light border border-saffron/20 rounded-2xl p-5 text-ink shadow-custom text-left">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-base">🎯</span>
              <h4 className="font-serif font-black text-xs text-saffron-dark uppercase tracking-wider">Demo Mode Form Templates</h4>
            </div>
            <p className="text-[10px] text-ink-light leading-relaxed mb-4">
              Select a preloaded configuration template. This instantiates realistic OCR field structures, confidence levels, validation scores, and layout bounding contexts.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {[
                { key: 'healthcare', label: '🏥 Patient Registration Form' },
                { key: 'education', label: '🎓 Student Admission Form' },
                { key: 'government', label: '🏛 Government KYC Application' },
                { key: 'banking', label: '💳 Banking Account KYC' }
              ].map((opt) => (
                <button
                  key={opt.key}
                  onClick={async () => {
                    setLoading(true);
                    try {
                      const token = localStorage.getItem('token');
                      const res = await axios.post('/api/forms/demo', { form_key: opt.key }, {
                        headers: { Authorization: `Bearer ${token}` }
                      });
                      showToast(`Preloaded ${opt.key} form created successfully!`, 'success');
                      navigate(`/analyze/${res.data.form_id}`);
                    } catch (err) {
                      showToast(err.response?.data?.message || 'Failed to create demo form.', 'error');
                    } finally {
                      setLoading(false);
                    }
                  }}
                  className="bg-white hover:bg-paper border border-paper-darker rounded-xl p-3 text-left text-xs font-bold text-ink-medium hover:border-teal hover:text-teal transition-all flex items-center justify-between shadow-sm"
                >
                  <span>{opt.label}</span>
                  <span className="text-teal font-black text-sm">→</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Analytics Brief Section */}
      {analytics && analytics.total_forms > 0 && (
        <div className="max-w-4xl mx-auto px-6 mt-12 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white border border-paper-darker p-5 rounded-xl text-center shadow-sm-custom">
            <h4 className="text-teal font-serif font-black text-3xl">{analytics.total_forms}</h4>
            <p className="text-[10px] text-ink-light mt-1 font-bold uppercase tracking-wider">Forms Analyzed</p>
          </div>
          <div className="bg-white border border-paper-darker p-5 rounded-xl text-center shadow-sm-custom">
            <h4 className="text-green font-serif font-black text-3xl">{analytics.validation_success_rate}%</h4>
            <p className="text-[10px] text-ink-light mt-1 font-bold uppercase tracking-wider font-semibold">Valid Entries Rate</p>
          </div>
          <div className="bg-white border border-paper-darker p-5 rounded-xl text-center shadow-sm-custom">
            <h4 className="text-saffron-dark font-serif font-black text-3xl">
              {Object.keys(analytics.categories || {}).length}
            </h4>
            <p className="text-[10px] text-ink-light mt-1 font-bold uppercase tracking-wider">Form Types</p>
          </div>
          <div className="bg-white border border-paper-darker p-5 rounded-xl text-center shadow-sm-custom">
            <h4 className="text-red font-serif font-black text-3xl">
              {analytics.field_status.errors}
            </h4>
            <p className="text-[10px] text-ink-light mt-1 font-bold uppercase tracking-wider font-semibold">Errors Pending</p>
          </div>
        </div>
      )}

      {/* Recently Analyzed Dashboard Table */}
      {analytics && analytics.recent_forms.length > 0 && (
        <div className="max-w-4xl mx-auto px-6 mt-12">
          <div className="flex items-center justify-between mb-4 border-b border-paper-darker pb-2">
            <h3 className="font-serif font-bold text-lg text-ink">Recently Analyzed Documents</h3>
            <Link to="/dashboard" className="text-xs font-bold text-teal hover:underline">View All</Link>
          </div>

          <div className="grid gap-3">
            {analytics.recent_forms.map((form) => (
              <div
                key={form.id}
                onClick={() => navigate(`/analyze/${form.id}`)}
                className="bg-white hover:bg-paper-dark/10 border border-paper-darker rounded-xl p-4 flex justify-between items-center shadow-sm-custom cursor-pointer transition-all"
              >
                <div className="flex items-center gap-3">
                  <div className="bg-teal-light p-2.5 rounded-lg text-teal">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-sm text-ink">{form.filename}</h4>
                    <p className="text-xs text-ink-light flex items-center gap-1.5 mt-0.5">
                      <span className="font-semibold">{form.form_type}</span> · {new Date(form.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-[10px] font-bold text-ink">Difficulty</div>
                    <div className="text-xs font-black text-saffron-dark">{form.difficulty_score} / 10</div>
                  </div>
                  <button className="bg-paper hover:bg-paper-dark border border-paper-darker text-xs font-bold px-3 py-1.5 rounded-lg transition-colors">
                    Open
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {cameraActive && (
        <CameraCapture
          onCapture={handleCameraCapture}
          onClose={() => setCameraActive(false)}
        />
      )}
    </div>
  );
}

// Side-by-Side Form Analyze View
function Analyze({ lang, showToast }) {
  const { formId } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState(null);
  const [selectedField, setSelectedField] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [expLoading, setExpLoading] = useState(false);
  const [editingValue, setEditingValue] = useState('');
  const [savingFieldId, setSavingFieldId] = useState(null);
  const [speechLanguage, setSpeechLanguage] = useState(lang);
  const [rightPanelTab, setRightPanelTab] = useState('guidance'); // 'guidance' or 'review_queue'
  const guidanceContainerRef = useRef(null);

  useEffect(() => {
    if (guidanceContainerRef.current) {
      guidanceContainerRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [selectedField?.id, explanation]);

  const getFillableFields = (fields) => {
    if (!fields) return [];
    return fields.filter(f => {
      const labelLower = (f.label || '').toLowerCase();
      const typeLower = (f.detected_type || '').toLowerCase();
      
      const isOfficeUse = /office\s*use|official\s*use|internal\s*use|admin\s*use|verified\s*by|reviewed\s*by|reviewer|remarks|approver|approved|verification|check\s*by/i.test(labelLower);
      const isChecklist = /checklist|enclosed|upload|attached|attachment|document/i.test(labelLower) || typeLower.includes('document');
      const isSignature = /signature|sign\s*here|candidate's\s*sign|applicant's\s*sign|signed/i.test(labelLower) || typeLower === 'signature';
      
      const SECTION_KEYWORDS_LOWER = [
        "personal information", "personal details", "profile details",
        "contact information", "contact details", "address details",
        "parent guardian information", "parent/guardian details", "family details",
        "academic information", "educational details", "academic background",
        "medical information", "medical history", "clinical details", "health declaration",
        "identification details", "identity details", "kyc details", "identity proof",
        "documents uploaded", "documents enclosed", "required documents", "attachments", "checklist", "document checklist",
        "declaration", "undertaking", "consent",
        "for office use only", "office use only", "official use", "internal use only",
        "employment history", "work experience", "employment details",
        "billing details", "payment details", "card details",
        "travel details", "itinerary details", "passenger information",
        "membership details", "membership plan", "subscription details",
        "policy details", "insurance details", "nominee details",
        "business details", "company details", "organization details",
        "legal declaration", "agreement terms"
      ];
      const isSectionHeader = SECTION_KEYWORDS_LOWER.some(kw => labelLower === kw || labelLower.startsWith(kw + ":") || labelLower.endsWith(kw));
      
      return !(isOfficeUse || isChecklist || isSignature || isSectionHeader);
    });
  };

  const fetchFormDetails = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`/api/forms/${formId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setForm(res.data);
      
      // Auto select first fillable field if not selected
      const fillable = getFillableFields(res.data.fields);
      if (fillable.length > 0 && !selectedField) {
        setSelectedField(fillable[0]);
      } else if (selectedField) {
        const fresh = res.data.fields.find(f => f.id === selectedField.id);
        if (fresh) {
          setSelectedField(fresh);
        }
      }
    } catch (err) {
      console.error(err);
      showToast('Error loading form details.', 'error');
    }
  };

  useEffect(() => {
    fetchFormDetails();
  }, [formId]);

  useEffect(() => {
    if (selectedField) {
      window.speechSynthesis.cancel();
      fetchFieldExplanation(selectedField.id);
      setEditingValue(selectedField.current_value || '');
    }
  }, [selectedField, lang]);

  const fetchFieldExplanation = async (fieldId) => {
    setExpLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`/api/forms/field/${fieldId}/explain?lang=${lang}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setExplanation(res.data.explanation);
    } catch (err) {
      console.error(err);
    } finally {
      setExpLoading(false);
    }
  };

  const handleFieldValueUpdate = async (fieldId) => {
    setSavingFieldId(fieldId);
    try {
      const token = localStorage.getItem('token');
      await axios.put(`/api/forms/field/${fieldId}`, {
        value: editingValue
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      showToast("Field updated and re-validated!", "success");
      await fetchFormDetails();
    } catch (err) {
      console.error(err);
      showToast("Failed to save field value.", "error");
    } finally {
      setSavingFieldId(null);
    }
  };

  // TTS Voice Synthesizer
  const handleReadAloud = () => {
    if (!explanation) return;

    window.speechSynthesis.cancel();

    const speechText = `${selectedField ? selectedField.label : ''}. ${explanation.what || ''}. ${explanation.input_guidance || ''}`;
    const utterance = new SpeechSynthesisUtterance(speechText);

    const voices = window.speechSynthesis.getVoices();
    let selectedVoice = null;

    if (speechLanguage === 'hi') {
      selectedVoice = voices.find(v => v.lang.toLowerCase().includes('hi'));
    } else if (speechLanguage === 'mr') {
      selectedVoice = voices.find(v => v.lang.toLowerCase().includes('mr'));
    } else {
      selectedVoice = voices.find(v => v.lang.toLowerCase().startsWith('en'));
    }

    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }

    window.speechSynthesis.speak(utterance);
  };

  if (!form) {
    return (
      <div className="min-h-[calc(100vh-64px)] flex items-center justify-center">
        <RefreshCw className="w-8 h-8 text-teal animate-spin" />
      </div>
    );
  }

  const fillableFields = getFillableFields(form.fields);
  const completedFields = fillableFields.filter(f => f.status === 'done').length;

  // Filter review queue fields
  const reviewFields = form.fields.filter(f => {
    const ocrConf = f.ocr_confidence !== undefined && f.ocr_confidence !== null ? f.ocr_confidence : f.confidence_score;
    const valScore = f.validation_score !== undefined && f.validation_score !== null ? f.validation_score : 100;
    return (ocrConf < 0.70) || (valScore < 80);
  });

  return (
    <div className="flex flex-col md:flex-row h-auto md:h-[calc(100vh-64px)] overflow-y-auto md:overflow-hidden bg-paper">

      {/* 1. LEFT PANEL: Fields List */}
      <div className="w-full md:w-80 bg-white border-r border-paper-darker flex flex-col h-[280px] md:h-full overflow-hidden flex-shrink-0">
        <div className="p-4 border-b border-paper-darker flex-shrink-0 space-y-3">
          <div>
            <h3 className="font-serif font-black text-sm text-ink truncate">{form.filename}</h3>
            <p className="text-[10px] text-ink-light mt-0.5 font-bold uppercase tracking-wider">{form.form_type}</p>
          </div>

          {/* Completeness Ring component */}
          <CompletenessRing completed={completedFields} total={fillableFields.length} />
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {fillableFields.map((f) => {
            const isActive = selectedField?.id === f.id;
            return (
              <div
                key={f.id}
                onClick={() => setSelectedField(f)}
                className={`flex items-start gap-2.5 p-3 rounded-lg cursor-pointer border transition-all duration-300 ${isActive
                    ? 'bg-teal-light/40 border-teal shadow-sm scale-[1.01] ring-1 ring-teal/20'
                    : f.status === 'error'
                      ? 'border-red/10 bg-red-light/20 hover:bg-paper hover:border-red/20'
                      : 'border-transparent hover:bg-paper hover:border-paper-darker'
                  }`}
              >
                <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold mt-0.5 flex-shrink-0 ${f.status === 'done'
                    ? 'bg-green text-white'
                    : f.status === 'error'
                      ? 'bg-red text-white'
                      : 'bg-paper-darker text-ink-medium'
                  }`}>
                  {f.status === 'done' ? '✓' : f.status === 'error' ? '!' : '•'}
                </div>
                <div className="flex-1 min-w-0">
                  <div className={`text-xs font-bold truncate ${isActive ? 'text-teal' : 'text-ink'}`}>{f.label}</div>
                  <div className="text-[10px] text-ink-light truncate mt-0.5">{f.current_value || 'Not filled yet'}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 2. MIDDLE PANEL: Paper Form Interactive Editor */}
      <div className="flex-1 bg-paper flex flex-col h-[550px] md:h-full overflow-hidden border-r border-paper-darker flex-shrink-0">
        <div className="bg-paper-dark px-4 py-2 border-b border-paper-darker flex justify-between items-center flex-shrink-0">
          <span className="text-xs font-bold text-ink-medium">📄 Form Workspace Preview</span>
          <button
            onClick={() => navigate(`/results/${formId}`)}
            className="bg-teal hover:bg-teal-dark text-white text-xs font-bold px-4 py-1.5 rounded-lg shadow-sm transition-all"
          >
            Finish & View Summary
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="bg-white border border-paper-darker rounded-xl max-w-xl mx-auto shadow-custom overflow-hidden">
            <div className="bg-teal p-5 text-white flex items-start gap-3">
              <div className="text-2xl">🏛</div>
              <div>
                <h3 className="font-serif font-black text-sm leading-tight">{form.form_type} Application Portal</h3>
                <p className="text-[10px] text-teal-light mt-0.5">Fill and validate fields sequentially to complete submission</p>
              </div>
            </div>

            <div className="p-6 space-y-5">
              {fillableFields.map((f) => {
                const isSelected = selectedField?.id === f.id;
                return (
                  <div
                    key={f.id}
                    onClick={() => setSelectedField(f)}
                    className={`p-3 rounded-xl border-2 transition-all duration-300 cursor-pointer ${isSelected
                        ? 'bg-teal-light/35 border-teal animate-pulse-glow ring-2 ring-teal/35 scale-[1.01] shadow-md'
                        : f.status === 'error'
                          ? 'bg-red-light/20 border-red/30 hover:border-red/50'
                          : 'border-transparent hover:bg-paper/50'
                      }`}
                  >
                    <div className="flex justify-between items-center mb-1.5">
                      <label className="text-xs font-black uppercase tracking-wider text-ink-medium flex items-center gap-1">
                        {f.label} {f.is_required && <span className="text-red font-bold">*</span>}
                      </label>
                      <div className="flex items-center gap-1.5">
                        {getConfidenceBadge(f.ocr_confidence !== undefined && f.ocr_confidence !== null ? f.ocr_confidence : f.confidence_score)}
                        {f.field_detection_confidence !== undefined && f.field_detection_confidence !== null && (
                          <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full ${
                            f.field_detection_confidence >= 0.8 ? 'bg-teal-light text-teal' : 'bg-yellow-light text-yellow-800'
                          }`}>
                            Map: {Math.round(f.field_detection_confidence * 100)}%
                          </span>
                        )}
                        <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full ${f.is_required ? 'bg-red-light text-red' : 'bg-paper-darker text-ink-light'
                          }`}>
                          {f.is_required ? 'Req' : 'Opt'}
                        </span>
                      </div>
                    </div>

                    <div className="relative flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full flex-shrink-0 ${
                        f.status === 'done' ? 'bg-green' : f.status === 'error' ? 'bg-red animate-pulse' : 'bg-paper-darker'
                      }`}></span>
                      
                      <div className="flex-1">
                        {isSelected ? (
                          <div className="flex gap-2">
                            <input
                              type="text"
                              value={editingValue}
                              onChange={(e) => setEditingValue(e.target.value)}
                              onBlur={() => handleFieldValueUpdate(f.id)}
                              placeholder={`Enter ${f.label}...`}
                              className={`flex-1 border-b-2 bg-transparent py-1 text-sm font-sans font-semibold outline-none focus:border-teal text-ink ${f.status === 'error' ? 'border-red text-red' : 'border-paper-darker'
                                }`}
                              onClick={(e) => e.stopPropagation()}
                            />
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleFieldValueUpdate(f.id);
                              }}
                              className="bg-teal text-white px-2.5 py-1 text-xs rounded hover:bg-teal-dark transition-colors font-bold"
                            >
                              {savingFieldId === f.id ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : 'Save'}
                            </button>
                          </div>
                        ) : (
                          <div className={`py-1 text-sm font-mono border-b border-paper-darker ${f.current_value ? 'text-green font-bold' : 'text-ink-pale italic'
                            }`}>
                            {f.current_value || 'Click here to write...'}
                          </div>
                        )}
                      </div>
                    </div>

                    {f.status === 'error' && f.error_message && (
                      <div className="text-[10px] text-red font-bold mt-1.5 flex items-center gap-1">
                        <ShieldAlert className="w-3 h-3 flex-shrink-0" /> {f.error_message}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* 3. RIGHT PANEL: AI Explanation and Chat */}
      <div className="w-full md:w-[360px] bg-white border-t md:border-t-0 md:border-l border-paper-darker flex flex-col h-[650px] md:h-full overflow-hidden flex-shrink-0">
        {/* Showcase Panel Tab Selection */}
        <div className="p-2 border-b border-paper-darker bg-paper-dark flex-shrink-0 flex gap-2">
          <button
            onClick={() => setRightPanelTab('guidance')}
            className={`flex-1 py-2 text-center text-xs font-bold rounded-lg transition-all ${
              rightPanelTab === 'guidance' ? 'bg-teal text-white shadow-sm' : 'text-ink-medium hover:bg-paper-darker'
            }`}
          >
            💡 AI Guidance
          </button>
          <button
            onClick={() => setRightPanelTab('review_queue')}
            className={`flex-1 py-2 text-center text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
              rightPanelTab === 'review_queue' ? 'bg-teal text-white shadow-sm' : 'text-ink-medium hover:bg-paper-darker'
            }`}
          >
            📋 Review Queue ({reviewFields.length})
          </button>
        </div>

        {rightPanelTab === 'guidance' ? (
          <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
            {/* Scrollable Guidance Container */}
            <div 
              ref={guidanceContainerRef}
              className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth"
            >
              <div className="border-b border-paper-darker pb-2 flex-shrink-0">
                <span className="text-[9px] font-bold text-ink-light uppercase tracking-wider block mb-1">AI Field Guidance</span>
                <h3 className="font-serif font-black text-lg text-ink truncate">
                  {selectedField ? selectedField.label : 'Select a field'}
                </h3>
              </div>

              {expLoading ? (
                <div className="flex flex-col items-center justify-center py-10 gap-3">
                  <RefreshCw className="w-6 h-6 text-teal animate-spin" />
                  <span className="text-xs text-ink-light">Generating AI translation...</span>
                </div>
              ) : explanation ? (
                <div className="space-y-4">
                  <div className="border border-paper-darker bg-white rounded-xl overflow-hidden shadow-sm border-l-4 border-l-teal animate-slide-up [animation-delay:50ms]">
                    <div className="bg-paper-dark px-3 py-1.5 text-[9px] font-bold text-teal uppercase tracking-wider">What is this?</div>
                    <div className="p-3 text-xs leading-relaxed text-ink-medium">{explanation.what}</div>
                  </div>

                  <div className="border border-paper-darker bg-white rounded-xl overflow-hidden shadow-sm border-l-4 border-l-teal-medium animate-slide-up [animation-delay:100ms]">
                    <div className="bg-paper-dark px-3 py-1.5 text-[9px] font-bold text-teal-medium uppercase tracking-wider">📝 Input Guidance</div>
                    <div className="p-3 text-xs leading-relaxed text-ink-medium">{explanation.input_guidance}</div>
                  </div>

                  <div className="border border-paper-darker bg-white rounded-xl overflow-hidden shadow-sm border-l-4 border-l-indigo-500 animate-slide-up [animation-delay:150ms]">
                    <div className="bg-paper-dark px-3 py-1.5 text-[9px] font-bold text-indigo-600 uppercase tracking-wider">Why is this requested?</div>
                    <div className="p-3 text-xs leading-relaxed text-ink-medium">{explanation.why}</div>
                  </div>

                  <div className="border border-paper-darker bg-white rounded-xl overflow-hidden shadow-sm border-l-4 border-l-blue-500 animate-slide-up [animation-delay:200ms]">
                    <div className="bg-paper-dark px-3 py-1.5 text-[9px] font-bold text-blue-600 uppercase tracking-wider">🔢 Accepted Formats</div>
                    <div className="p-3 text-xs leading-relaxed font-semibold text-ink-medium">{explanation.formats}</div>
                  </div>

                  <div className="border border-paper-darker bg-white rounded-xl overflow-hidden shadow-sm border-l-4 border-l-green animate-slide-up [animation-delay:250ms]">
                    <div className="bg-paper-dark px-3 py-1.5 text-[9px] font-bold text-green uppercase tracking-wider">✅ Example Value</div>
                    <div className="p-3 text-xs font-mono text-green bg-green-light/20 whitespace-pre-wrap">{explanation.example}</div>
                  </div>

                  {explanation.mistakes && (
                    <div className="border border-paper-darker bg-white rounded-xl overflow-hidden shadow-sm border-l-4 border-l-saffron-dark animate-slide-up [animation-delay:300ms]">
                      <div className="bg-paper-dark px-3 py-1.5 text-[9px] font-bold text-saffron-dark uppercase tracking-wider">💡 Common Mistakes</div>
                      <div className="p-3 text-xs leading-relaxed text-ink-medium">{explanation.mistakes}</div>
                    </div>
                  )}

                  <div className="border border-paper-darker bg-white rounded-xl overflow-hidden shadow-sm border-l-4 border-l-red animate-slide-up [animation-delay:350ms]">
                    <div className="bg-paper-dark px-3 py-1.5 text-[9px] font-bold text-red uppercase tracking-wider">⚠️ Validation Rules</div>
                    <div className="p-3 text-xs leading-relaxed text-ink-medium">{explanation.validation}</div>
                  </div>

                  {/* Voice Read Aloud Box */}
                  <div className="bg-paper border border-paper-darker rounded-xl p-3 flex flex-col gap-2 animate-slide-up [animation-delay:400ms]">
                    <div className="flex justify-between items-center">
                      <span className="text-[10px] font-bold text-ink-medium flex items-center gap-1">
                        <Volume2 className="w-3.5 h-3.5 text-teal" /> Listen to explanation
                      </span>
                      <select
                        value={speechLanguage}
                        onChange={(e) => setSpeechLanguage(e.target.value)}
                        className="text-[10px] bg-white border border-paper-darker outline-none rounded p-0.5"
                      >
                        <option value="en">English Voice</option>
                        <option value="hi">Hindi Voice (हिंदी)</option>
                        <option value="mr">Marathi Voice (मराठी)</option>
                      </select>
                    </div>
                    <button
                      onClick={handleReadAloud}
                      className="bg-teal hover:bg-teal-dark text-white text-xs font-bold py-2 rounded-lg transition-colors flex items-center justify-center gap-1.5 shadow-sm"
                    >
                      <Play className="w-3 h-3 fill-current" /> Speak Explanation
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-center text-xs text-ink-light py-10 flex flex-col items-center gap-2">
                  <HelpCircle className="w-6 h-6 text-paper-darker" />
                  <span>Select any field to view translation, plain-language definition, and voice assist.</span>
                </div>
              )}
            </div>

            {/* Smart Assistant */}
            <div className="border-t border-paper-darker p-3 bg-paper-dark flex-shrink-0">
              <SmartAssistant formId={formId} lang={lang} />
            </div>
          </div>
        ) : (
          /* Needs Review Panel */
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-paper-dark/10">
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-[10px] text-amber-800 leading-relaxed font-semibold mb-2">
              ⚠️ Fields appear here if OCR confidence is below 70% or validation rules score is below 80/100.
            </div>
            
            {reviewFields.length === 0 ? (
              <div className="text-center py-10 flex flex-col items-center justify-center gap-2">
                <CheckCircle className="w-8 h-8 text-green" />
                <span className="text-xs font-bold text-ink">Clear review queue! All fields meet threshold requirements.</span>
              </div>
            ) : (
              reviewFields.map((f) => {
                const isEditing = selectedField?.id === f.id;
                const ocrConf = f.ocr_confidence !== undefined && f.ocr_confidence !== null ? f.ocr_confidence : f.confidence_score;
                const valScore = f.validation_score !== undefined && f.validation_score !== null ? f.validation_score : 100;
                
                let issue = "";
                let suggestedFix = "Double check layout characters and input correct value.";
                
                if (ocrConf < 0.70) {
                  issue += `Low OCR Confidence (${Math.round(ocrConf * 100)}%)`;
                }
                if (valScore < 80) {
                  if (issue) issue += " & ";
                  issue += `Validation Error (${valScore}/100): ${f.error_message || 'Format matches incorrect constraints.'}`;
                  
                  const t = f.detected_type || '';
                  if (t.includes('phone')) suggestedFix = "Provide a valid 10-digit phone number.";
                  else if (t.includes('email')) suggestedFix = "Provide a valid email (e.g. name@domain.com).";
                  else if (t.includes('pin') || t.includes('zip')) suggestedFix = "Provide a valid 6-digit PIN code.";
                  else if (t.includes('aadhaar')) suggestedFix = "Provide a 12-digit Aadhaar number.";
                  else if (t.includes('pan')) suggestedFix = "Provide a 10-character alphanumeric PAN.";
                  else if (t.includes('ifsc')) suggestedFix = "Provide an 11-character IFSC code.";
                  else if (t.includes('dob')) suggestedFix = "Provide a valid date of birth (e.g. DD/MM/YYYY).";
                }
                
                return (
                  <div 
                    key={f.id}
                    className={`border rounded-xl p-3 bg-white shadow-sm flex flex-col gap-2 transition-all cursor-pointer ${
                      isEditing ? 'border-teal ring-1 ring-teal/30' : 'border-paper-darker'
                    }`}
                    onClick={() => {
                      setSelectedField(f);
                      setEditingValue(f.current_value || '');
                    }}
                  >
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold text-ink">{f.label}</span>
                      <span className="text-[9px] bg-red-light text-red px-2 py-0.5 rounded-full font-bold border border-red/10">Review</span>
                    </div>
                    
                    <div className="text-[10px]">
                      <span className="font-bold text-ink-light block uppercase tracking-wider text-[8px]">Detected Value</span>
                      <span className="font-mono bg-paper px-1.5 py-0.5 rounded block mt-0.5 text-red font-semibold">{f.current_value || '[Empty]'}</span>
                    </div>
                    
                    <div className="text-[10px] text-red bg-red-light p-2 rounded border border-red/10">
                      <span className="font-bold block uppercase tracking-wider text-[8px]">Issue</span>
                      <p className="mt-0.5 font-sans leading-normal">{issue}</p>
                    </div>
                    
                    <div className="text-[10px] text-teal-medium bg-teal-light/50 p-2 rounded border border-teal/10">
                      <span className="font-bold block uppercase tracking-wider text-[8px]">Suggested Fix</span>
                      <p className="mt-0.5 font-sans leading-normal">{suggestedFix}</p>
                    </div>
                    
                    {isEditing && (
                      <div className="flex gap-1.5 mt-1 border-t border-paper-light pt-2">
                        <input
                          type="text"
                          value={editingValue}
                          onChange={(e) => setEditingValue(e.target.value)}
                          placeholder={`Correct ${f.label}`}
                          className="flex-1 text-xs border border-paper-darker rounded px-2 py-1 outline-none focus:border-teal"
                          onClick={(e) => e.stopPropagation()}
                        />
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleFieldValueUpdate(f.id);
                          }}
                          className="bg-teal text-white text-[10px] font-bold px-2 py-1 rounded hover:bg-teal-dark transition-colors"
                        >
                          {savingFieldId === f.id ? 'Saving...' : 'Resolve'}
                        </button>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// Summary & Results Dashboard
function Results({ showToast }) {
  const { formId } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState(null);
  const [checkedDocs, setCheckedDocs] = useState({});

  useEffect(() => {
    async function fetchResults() {
      try {
        const token = localStorage.getItem('token');
        const res = await axios.get(`/api/forms/${formId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setForm(res.data);
      } catch (err) {
        console.error(err);
      }
    }
    fetchResults();
  }, [formId]);

  const toggleDoc = (docName) => {
    setCheckedDocs(prev => ({
      ...prev,
      [docName]: !prev[docName]
    }));
  };

  if (!form) {
    return (
      <div className="min-h-[calc(100vh-64px)] flex items-center justify-center">
        <RefreshCw className="w-8 h-8 text-teal animate-spin" />
      </div>
    );
  }

  const errorFields = form.fields.filter(f => f.status === 'error');
  const validFields = form.fields.filter(f => f.status === 'done');

  // Calculate average confidence scores for the summary dashboard
  const ocrConfidences = form.fields.map(f => f.ocr_confidence !== undefined && f.ocr_confidence !== null ? f.ocr_confidence : f.confidence_score).filter(c => c !== undefined && c !== null);
  const avgOcrConf = ocrConfidences.length > 0 ? ocrConfidences.reduce((a, b) => a + b, 0) / ocrConfidences.length : 0.85;

  const mappingConfidences = form.fields.map(f => f.field_detection_confidence).filter(c => c !== undefined && c !== null);
  const avgMappingConf = mappingConfidences.length > 0 ? mappingConfidences.reduce((a, b) => a + b, 0) / mappingConfidences.length : 0.90;

  const ocrAccuracy = form.summary?.ocr_accuracy !== undefined ? form.summary.ocr_accuracy : avgOcrConf;
  const fieldDetection = form.summary?.field_detection_confidence !== undefined ? form.summary.field_detection_confidence : 0.90;
  const fieldMapping = form.summary?.field_mapping_confidence !== undefined ? form.summary.field_mapping_confidence : avgMappingConf;
  const classConf = form.summary?.classification_confidence !== undefined ? form.summary.classification_confidence : 0.85;

  return (
    <div className="max-w-4xl mx-auto px-6 py-10 space-y-6">

      {/* 1. HERO COMPLETION RING */}
      <div className="bg-teal text-white rounded-2xl p-6 md:p-8 flex flex-col md:flex-row items-center gap-6 shadow-lg-custom">
        <div className="flex gap-4 flex-shrink-0 items-center">
          <div className="w-16 h-16 rounded-full border-4 border-saffron-light/20 flex flex-col items-center justify-center bg-teal-dark/50 flex-shrink-0">
            <span className="font-serif font-black text-2xl text-saffron">{form.difficulty_score}</span>
            <span className="text-[8px] font-bold text-teal-light tracking-wide uppercase">Diff</span>
          </div>
          
          <div className="bg-teal-dark/40 rounded-xl p-1 shadow-sm border border-teal-medium">
            <CompletenessRing 
              completed={validFields.length} 
              total={form.fields.length} 
              compact={true}
            />
          </div>
        </div>

        <div className="flex-1 text-center md:text-left">
          <h2 className="font-serif font-black text-xl md:text-2xl mb-1">{form.filename} — Analysis</h2>
          <p className="text-xs text-teal-light leading-relaxed max-w-lg">
            AI analyzed all {form.fields.length} form inputs. We predicted {form.predicted_documents.length} required documents.{' '}
            {errorFields.length > 0 ? (
              <span className="text-saffron font-bold font-sans">
                {errorFields.length} format issues need your correction.
              </span>
            ) : (
              <span className="text-green-light font-bold font-sans">
                Excellent! All mandatory fields are valid.
              </span>
            )}
          </p>
        </div>
        <div className="flex flex-col gap-2.5 flex-shrink-0">
          <button
            onClick={() => navigate(`/analyze/${formId}`)}
            className="bg-saffron hover:bg-saffron-dark text-white text-xs font-bold px-5 py-2.5 rounded-lg shadow-sm flex items-center justify-center gap-1.5 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Go back & Edit
          </button>
        </div>
      </div>

      {/* Confidence Dashboard Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        {/* Card 1: Form Classification */}
        <div 
          className="bg-white border border-paper-darker p-4 rounded-xl flex items-center gap-3.5 shadow-sm-custom hover:shadow-md transition-shadow cursor-help"
          title="Form Classification: ML and keyword categorizer match probability."
        >
          <div className="w-10 h-10 rounded-lg bg-teal-light/50 text-teal flex items-center justify-center font-bold text-lg font-sans">📁</div>
          <div>
            <div className="text-[10px] text-ink-light font-bold uppercase tracking-wider">Form Classification</div>
            <div className="text-xs font-black text-ink">{form.form_type}</div>
            <div className="text-[10px] text-teal font-bold">{Math.round(classConf * 100)}% Confidence</div>
          </div>
        </div>
        
        {/* Card 2: OCR Accuracy */}
        <div 
          className="bg-white border border-paper-darker p-4 rounded-xl flex items-center gap-3.5 shadow-sm-custom hover:shadow-md transition-shadow cursor-help"
          title="OCR Accuracy: Average confidence of text blocks extracted by the OCR engine."
        >
          <div className="w-10 h-10 rounded-lg bg-green-light text-green flex items-center justify-center font-bold text-lg font-sans">🔍</div>
          <div>
            <div className="text-[10px] text-ink-light font-bold uppercase tracking-wider">OCR Accuracy</div>
            <div className="text-xs font-black text-ink">{Math.round(ocrAccuracy * 100)}%</div>
            <div className="text-[10px] text-green font-bold">Text recognition rate</div>
          </div>
        </div>

        {/* Card 3: Field Detection */}
        <div 
          className="bg-white border border-paper-darker p-4 rounded-xl flex items-center gap-3.5 shadow-sm-custom hover:shadow-md transition-shadow cursor-help"
          title="Field Detection: Quality of inputs identification against form labels and rules."
        >
          <div className="w-10 h-10 rounded-lg bg-teal-light text-teal flex items-center justify-center font-bold text-lg font-sans">📋</div>
          <div>
            <div className="text-[10px] text-ink-light font-bold uppercase tracking-wider">Field Detection</div>
            <div className="text-xs font-black text-ink">{Math.round(fieldDetection * 100)}%</div>
            <div className="text-[10px] text-teal font-bold">Input detection rate</div>
          </div>
        </div>

        {/* Card 4: Field Mapping */}
        <div 
          className="bg-white border border-paper-darker p-4 rounded-xl flex items-center gap-3.5 shadow-sm-custom hover:shadow-md transition-shadow cursor-help"
          title="Field Mapping: Structural mapping score based on horizontal and vertical alignment spacing."
        >
          <div className="w-10 h-10 rounded-lg bg-saffron-light text-saffron-dark flex items-center justify-center font-bold text-lg font-sans">📍</div>
          <div>
            <div className="text-[10px] text-ink-light font-bold uppercase tracking-wider">Field Mapping Score</div>
            <div className="text-xs font-black text-ink">{Math.round(fieldMapping * 100)}%</div>
            <div className="text-[10px] text-saffron-dark font-bold">Pairing alignment</div>
          </div>
        </div>
      </div>

      {/* Dynamic Summary Stats Panel with Export Deck */}
      <div className="bg-white border border-paper-darker rounded-xl p-5 shadow-sm-custom flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h4 className="font-serif font-black text-sm text-ink mb-0.5">📥 Export Validated Data Reports</h4>
          <p className="text-[10px] text-ink-light">Download a high-fidelity ReportLab US Letter PDF summary or clean JSON mappings.</p>
        </div>
        
        <div className="flex gap-2 w-full sm:w-auto">
          <button
            onClick={async () => {
              try {
                const token = localStorage.getItem('token');
                const res = await axios.get(`/api/forms/${formId}/export/pdf`, {
                  headers: { Authorization: `Bearer ${token}` },
                  responseType: 'blob'
                });
                const blob = new Blob([res.data], { type: 'application/pdf' });
                const link = document.createElement('a');
                link.href = window.URL.createObjectURL(blob);
                link.download = `${form.filename}_report.pdf`;
                link.click();
                showToast("PDF report downloaded successfully!", "success");
              } catch (err) {
                showToast("Failed to export PDF report.", "error");
              }
            }}
            className="flex-1 sm:flex-initial bg-teal hover:bg-teal-dark text-white text-xs font-bold px-4 py-2.5 rounded-lg shadow-sm flex items-center justify-center gap-1.5 transition-all cursor-pointer"
          >
            📄 Download PDF
          </button>
          
          <button
            onClick={async () => {
              try {
                const token = localStorage.getItem('token');
                const res = await axios.get(`/api/forms/${formId}/export/json`, {
                  headers: { Authorization: `Bearer ${token}` }
                });
                const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(JSON.stringify(res.data, null, 2))}`;
                const link = document.createElement('a');
                link.href = jsonString;
                link.download = `${form.filename}_schema.json`;
                link.click();
                showToast("JSON schema exported successfully!", "success");
              } catch (err) {
                showToast("Failed to export JSON schema.", "error");
              }
            }}
            className="flex-1 sm:flex-initial bg-paper hover:bg-paper-dark border border-paper-darker text-ink text-xs font-bold px-4 py-2.5 rounded-lg shadow-sm flex items-center justify-center gap-1.5 transition-all cursor-pointer"
          >
            ⚙️ Export JSON
          </button>
        </div>
      </div>

      {/* Inline explanation of confidence calculations */}
      <div className="bg-paper-dark/30 border border-paper-darker rounded-xl p-4 text-[11px] text-ink-light leading-relaxed">
        <h5 className="font-bold text-ink mb-1">ℹ️ Understanding Confidence Metrics</h5>
        <ul className="list-disc list-inside space-y-1">
          <li><strong>Form Classification:</strong> Calculated using a hybrid Naive Bayes classifier boost mapping relative keywords frequency to classify forms.</li>
          <li><strong>OCR Accuracy:</strong> The geometric mean of prediction confidences returned by the character recognizer.</li>
          <li><strong>Field Detection:</strong> Measures matching densities of form inputs versus labeled descriptors.</li>
          <li><strong>Field Mapping:</strong> Measures layout alignment correctness within columns and sections.</li>
        </ul>
      </div>

      {/* 2. THREE PANELS GRID */}
      <div className="grid md:grid-cols-2 gap-6">

        {/* Validation Errors Box */}
        <div className="bg-white border border-paper-darker rounded-xl p-5 shadow-sm-custom flex flex-col">
          <div className="flex justify-between items-center border-b border-paper-darker pb-2.5 mb-4 flex-shrink-0">
            <h3 className="font-serif font-bold text-sm text-ink flex items-center gap-1.5">
              <ShieldAlert className="w-4.5 h-4.5 text-red" /> Form Validation Report
            </h3>
            <span className="bg-red-light text-red text-[10px] font-bold px-2 py-0.5 rounded-full">
              {errorFields.length} issues
            </span>
          </div>

          <div className="flex-1 space-y-3">
            {errorFields.length > 0 ? (
              errorFields.map((f) => (
                <div key={f.id} className="bg-red-light/35 border border-red/10 rounded-lg p-3 flex gap-2.5 items-start">
                  <AlertTriangle className="w-4 h-4 text-red flex-shrink-0 mt-0.5" />
                  <div>
                    <h5 className="text-xs font-bold text-red">{f.label}</h5>
                    <p className="text-[10px] text-ink-medium mt-0.5 leading-relaxed">{f.error_message || 'Format matches incorrect constraints.'}</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="flex flex-col items-center justify-center py-10 gap-2 text-green">
                <CheckCircle className="w-8 h-8" />
                <span className="text-xs font-bold">No format errors found. Ready for submission!</span>
              </div>
            )}
          </div>
        </div>

        {/* Predicted Documents Checklist */}
        <div className="bg-white border border-paper-darker rounded-xl p-5 shadow-sm-custom flex flex-col">
          <div className="flex justify-between items-center border-b border-paper-darker pb-2.5 mb-4 flex-shrink-0">
            <h3 className="font-serif font-bold text-sm text-ink flex items-center gap-1.5">
              <FileCheck className="w-4.5 h-4.5 text-teal" /> Document Checklist
            </h3>
            <span className="bg-teal-light text-teal text-[10px] font-bold px-2 py-0.5 rounded-full">
              AI Predicted
            </span>
          </div>

          <div className="flex-1 space-y-2">
            {form.predicted_documents.map((doc, idx) => {
              const isChecked = checkedDocs[doc.name];
              return (
                <div
                  key={idx}
                  onClick={() => toggleDoc(doc.name)}
                  className={`border border-paper-darker rounded-lg p-3 flex items-start gap-3 cursor-pointer transition-all ${isChecked ? 'bg-green-light/25 border-green' : 'hover:bg-paper'
                    }`}
                >
                  <div className={`w-4 h-4 rounded border flex items-center justify-center flex-shrink-0 mt-0.5 transition-all ${isChecked ? 'bg-green border-green text-white' : 'border-paper-darker bg-white'
                    }`}>
                    {isChecked && '✓'}
                  </div>
                  <div>
                    <h5 className={`text-xs font-bold ${isChecked ? 'text-green line-through' : 'text-ink'}`}>{doc.name}</h5>
                    <p className="text-[10px] text-ink-light mt-0.5 leading-relaxed">{doc.hint}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

      </div>

      {/* 3. DYNAMIC AI FORM SUMMARY */}
      {form.summary && (
        <div className="bg-white border border-paper-darker rounded-xl p-6 shadow-sm-custom space-y-4">
          <h3 className="font-serif font-black text-md text-ink pb-2 border-b border-paper-darker">📋 Dynamic AI Form Summary</h3>
          <div className="grid md:grid-cols-2 gap-6 text-xs text-ink-medium leading-relaxed">
            <div className="space-y-3.5">
              <div>
                <strong className="block text-ink uppercase tracking-wider text-[9px] mb-0.5">Purpose of Form</strong>
                <p>{form.summary.purpose}</p>
              </div>
              <div>
                <strong className="block text-ink uppercase tracking-wider text-[9px] mb-0.5">Who should fill it?</strong>
                <p>{form.summary.who}</p>
              </div>
            </div>
            <div className="space-y-3.5">
              <div>
                <strong className="block text-ink uppercase tracking-wider text-[9px] mb-0.5">Estimated completion time</strong>
                <p>{form.summary.est_time}</p>
              </div>
              <div>
                <strong className="block text-red uppercase tracking-wider text-[9px] mb-0.5">Important warnings</strong>
                <p className="text-red font-semibold">{form.summary.warnings}</p>
              </div>
            </div>
            {form.summary.classification_reason && (
              <div className="md:col-span-2 border-t border-paper-darker pt-4 mt-2">
                <strong className="block text-teal uppercase tracking-wider text-[9px] mb-0.5">AI Classification Analysis</strong>
                <p className="text-xs text-ink-medium font-bold">
                  Classified as <span className="text-teal font-serif font-black">{form.form_type}</span> with{' '}
                  <span className="text-green font-bold">{Math.round((form.summary.classification_confidence || 0) * 100)}% confidence</span>.
                </p>
                <p className="text-xs text-ink-light mt-1 italic">
                  Reasoning: {form.summary.classification_reason}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Analytics History Dashboard Component
function HistoryDashboard({ showToast }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedForms, setSelectedForms] = useState([]);
  const [compareModalOpen, setCompareModalOpen] = useState(false);

  useEffect(() => {
    async function fetchAnalytics() {
      try {
        const token = localStorage.getItem('token');
        const res = await axios.get('/api/analytics', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setAnalytics(res.data);
      } catch (err) {
        console.error(err);
        showToast("Error loading analytics data.", "error");
      } finally {
        setLoading(false);
      }
    }
    fetchAnalytics();
  }, []);

  const handleSelectForm = (form) => {
    setSelectedForms(prev => {
      const isSelected = prev.find(x => x.id === form.id);
      if (isSelected) {
        return prev.filter(x => x.id !== form.id);
      } else {
        if (prev.length >= 2) {
          showToast("You can only select up to 2 forms for comparison.", "error");
          return prev;
        }
        return [...prev, form];
      }
    });
  };

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-64px)] flex items-center justify-center">
        <RefreshCw className="w-8 h-8 text-teal animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-10 space-y-8">
      <div>
        <h2 className="font-serif font-black text-2xl text-ink">Personal Analytics Dashboard</h2>
        <p className="text-xs text-ink-light">Overview of your analyzed documents, validation rates, and system logs.</p>
      </div>

      {analytics && (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white border border-paper-darker p-5 rounded-xl text-center shadow-sm-custom">
              <h4 className="text-teal font-serif font-black text-3xl">{analytics.total_forms}</h4>
              <p className="text-[9px] text-ink-light mt-1 font-bold uppercase tracking-wider">Forms Analyzed</p>
            </div>
            <div className="bg-white border border-paper-darker p-5 rounded-xl text-center shadow-sm-custom">
              <h4 className="text-green font-serif font-black text-3xl">{analytics.validation_success_rate}%</h4>
              <p className="text-[9px] text-ink-light mt-1 font-bold uppercase tracking-wider">Accuracy Score</p>
            </div>
            <div className="bg-white border border-paper-darker p-5 rounded-xl text-center shadow-sm-custom">
              <h4 className="text-saffron-dark font-serif font-black text-3xl">{analytics.field_status.done}</h4>
              <p className="text-[9px] text-ink-light mt-1 font-bold uppercase tracking-wider">Fields Completed</p>
            </div>
            <div className="bg-white border border-paper-darker p-5 rounded-xl text-center shadow-sm-custom">
              <h4 className="text-red font-serif font-black text-3xl">{analytics.field_status.errors}</h4>
              <p className="text-[9px] text-ink-light mt-1 font-bold uppercase tracking-wider">Errors Pending</p>
            </div>
          </div>

          {/* Project Health Dashboard Widget */}
          <div className="bg-white border border-paper-darker rounded-xl p-5 shadow-sm-custom space-y-4">
            <div className="flex justify-between items-center border-b border-paper-darker pb-2.5">
              <h3 className="font-serif font-bold text-sm text-ink flex items-center gap-2">
                🩺 Platform Health & Quality Metrics
              </h3>
              <span className="bg-teal text-white text-[9px] font-bold px-2 py-0.5 rounded-full">
                OCR & User Corrections Analysis
              </span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-3 text-xs leading-normal">
                <div>
                  <span className="text-[10px] text-ink-light font-bold uppercase tracking-wider block">Average OCR Accuracy</span>
                  <p className="font-serif font-black text-lg text-teal">{analytics.avg_ocr_accuracy}%</p>
                  <span className="text-[9px] text-ink-light font-sans block mt-0.5">Average layout character recognition rate.</span>
                </div>
                <div>
                  <span className="text-[10px] text-ink-light font-bold uppercase tracking-wider block">User Correction Rate</span>
                  <p className="font-serif font-black text-lg text-saffron-dark">{analytics.correction_percentage}%</p>
                  <span className="text-[9px] text-ink-light font-sans block mt-0.5">
                    Percentage of fields user modified from original OCR output ({analytics.fields_corrected} fields corrected).
                  </span>
                </div>
              </div>
              
              <div className="space-y-3 text-xs leading-normal">
                <div>
                  <span className="text-[10px] text-ink-light font-bold uppercase tracking-wider block">Validation Success Rate</span>
                  <p className="font-serif font-black text-lg text-green">{analytics.validation_success_rate}%</p>
                  <span className="text-[9px] text-ink-light font-sans block mt-0.5">Ratio of format-compliant entries.</span>
                </div>
                <div>
                  <span className="text-[10px] text-ink-light font-bold uppercase tracking-wider block">Multilingual Coverage</span>
                  <p className="font-serif font-black text-lg text-teal-medium">{analytics.languages_used} {analytics.languages_used === 1 ? 'Language' : 'Languages'}</p>
                  <span className="text-[9px] text-ink-light font-sans block mt-0.5">English, Hindi (हिंदी), and Marathi (मराठी).</span>
                </div>
              </div>

              {/* Top Fields Corrected */}
              <div className="space-y-2">
                <span className="text-[10px] text-ink-light font-bold uppercase tracking-wider block">Most Corrected Fields</span>
                {analytics.most_corrected && analytics.most_corrected.length > 0 ? (
                  <div className="space-y-1.5">
                    {analytics.most_corrected.map((item, idx) => (
                      <div key={idx} className="flex justify-between items-center bg-paper/30 border border-paper-darker rounded px-2 py-1 text-[10px]">
                        <span className="font-bold text-ink-medium capitalize">{item.type.replace('_', ' ')}</span>
                        <span className="text-saffron-dark font-mono font-bold">{item.count} edits</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <span className="text-xs text-ink-light italic">No field corrections registered yet.</span>
                )}
              </div>
            </div>
          </div>

          {/* Recharts Analytics Charts Panel */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Chart 1: OCR Accuracy Trend */}
            <div className="bg-white border border-paper-darker rounded-xl p-5 shadow-sm-custom">
              <h3 className="font-serif font-bold text-sm text-ink mb-4 pb-2 border-b border-paper-darker">OCR Accuracy & Validation Trends</h3>
              <div className="h-64 text-xs font-sans">
                {analytics.ocr_trend && analytics.ocr_trend.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={analytics.ocr_trend}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E5DDD1" />
                      <XAxis dataKey="name" stroke="#8A7D6A" />
                      <YAxis domain={[0, 100]} stroke="#8A7D6A" />
                      <Tooltip contentStyle={{ backgroundColor: '#F7F3ED', borderColor: '#E5DDD1' }} />
                      <Legend />
                      <Line name="OCR Accuracy %" type="monotone" dataKey="confidence" stroke="#F4A024" strokeWidth={2.5} activeDot={{ r: 6 }} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-ink-light">No trend data available yet.</div>
                )}
              </div>
            </div>

            {/* Chart 2: Category Distribution */}
            <div className="bg-white border border-paper-darker rounded-xl p-5 shadow-sm-custom">
              <h3 className="font-serif font-bold text-sm text-ink mb-4 pb-2 border-b border-paper-darker">Forms Category Distribution</h3>
              <div className="h-64 text-xs font-sans">
                {analytics.categories_distribution && analytics.categories_distribution.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={analytics.categories_distribution}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E5DDD1" />
                      <XAxis dataKey="category" stroke="#8A7D6A" />
                      <YAxis stroke="#8A7D6A" allowDecimals={false} />
                      <Tooltip contentStyle={{ backgroundColor: '#F7F3ED', borderColor: '#E5DDD1' }} />
                      <Bar name="Form Volume" dataKey="count" fill="#0D5C63" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-ink-light">No category distribution data available.</div>
                )}
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {/* History Table */}
            <div className="md:col-span-2 bg-white border border-paper-darker rounded-xl p-5 shadow-sm-custom flex flex-col">
              <div className="flex justify-between items-center border-b border-paper-darker pb-2 mb-4">
                <h3 className="font-serif font-bold text-sm text-ink">Document Upload History</h3>
                {selectedForms.length === 2 && (
                  <button 
                    onClick={() => setCompareModalOpen(true)}
                    className="bg-saffron hover:bg-saffron-dark text-white text-[10px] font-bold px-3 py-1 rounded transition-colors flex items-center gap-1 shadow-sm"
                  >
                    ⚖️ Compare Forms ({selectedForms.length})
                  </button>
                )}
              </div>

              <div className="space-y-3">
                {analytics.recent_forms.map(form => {
                  const isChecked = selectedForms.some(x => x.id === form.id);
                  return (
                    <div 
                      key={form.id} 
                      onClick={() => handleSelectForm(form)}
                      className={`flex justify-between items-center p-3 border rounded-lg transition-colors cursor-pointer ${
                        isChecked ? 'border-teal bg-teal-light/20' : 'border-paper-light bg-paper/10 hover:bg-paper-light'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={(e) => {
                            e.stopPropagation();
                            handleSelectForm(form);
                          }}
                          onClick={(e) => e.stopPropagation()}
                          className="accent-teal cursor-pointer w-4 h-4"
                        />
                        <div>
                          <h4 className="text-xs font-bold text-ink">{form.filename}</h4>
                          <p className="text-[9px] text-ink-light mt-0.5">{form.form_type} · {new Date(form.created_at).toLocaleDateString()}</p>
                        </div>
                      </div>
                      <Link
                        to={`/analyze/${form.id}`}
                        onClick={(e) => e.stopPropagation()}
                        className="bg-teal text-white text-[10px] font-bold px-3 py-1.5 rounded hover:bg-teal-dark transition-colors"
                      >
                        Open
                      </Link>
                    </div>
                  );
                })}
                {analytics.recent_forms.length === 0 && (
                  <p className="text-center text-xs text-ink-light py-6">No uploads found.</p>
                )}
              </div>
            </div>

            {/* System logs */}
            <div className="bg-white border border-paper-darker rounded-xl p-5 shadow-sm-custom">
              <h3 className="font-serif font-bold text-sm text-ink mb-4 pb-2 border-b border-paper-darker">Security & Activity Log</h3>
              <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
                {analytics.activity_logs.map((log, idx) => (
                  <div key={idx} className="text-[10px] leading-tight border-b border-paper-light pb-2 last:border-0">
                    <span className="font-bold text-teal block">{log.action}</span>
                    <p className="text-ink-medium mt-0.5">{log.details}</p>
                    <span className="text-[8px] text-ink-light font-mono block mt-1">{new Date(log.created_at).toLocaleTimeString()}</span>
                  </div>
                ))}
                {analytics.activity_logs.length === 0 && (
                  <p className="text-center text-[10px] text-ink-light py-4">No logged activity yet.</p>
                )}
              </div>
            </div>
          </div>
        </>
      )}

      {compareModalOpen && (
        <CompareModal 
          forms={selectedForms} 
          onClose={() => setCompareModalOpen(false)} 
          showToast={showToast}
        />
      )}
    </div>
  );
}

// Router Wrapper
export default function App() {
  const [user, setUser] = useState(null);
  const [lang, setLang] = useState(localStorage.getItem('lang') || 'en');
  const [loading, setLoading] = useState(true);
  const [demoMode, setDemoMode] = useState(localStorage.getItem('demoMode') === 'true');
  const [toast, setToast] = useState(null);

  // Accessibility Scaling and High Contrast states
  const [accessibility, setAccessibility] = useState({
    highContrast: localStorage.getItem('highContrast') === 'true',
    fontSize: localStorage.getItem('fontSize') || 'medium'
  });

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  // Auto Login check
  useEffect(() => {
    async function checkUser() {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const res = await axios.get('/api/auth/me', {
            headers: { Authorization: `Bearer ${token}` }
          });
          setUser(res.data.user);
        } catch (err) {
          localStorage.removeItem('token');
        }
      }
      setLoading(false);
    }
    checkUser();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    showToast("Logged out successfully.", "info");
  };

  const getFontSizeStyle = () => {
    if (accessibility.fontSize === 'large') return { fontSize: '18px' };
    if (accessibility.fontSize === 'xlarge') return { fontSize: '20px' };
    return {};
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-paper flex items-center justify-center">
        <RefreshCw className="w-8 h-8 text-teal animate-spin" />
      </div>
    );
  }

  return (
    <Router>
      <div 
        className={`min-h-screen bg-paper flex flex-col font-sans transition-all duration-300 ${
          accessibility.highContrast ? 'high-contrast' : ''
        }`}
        style={getFontSizeStyle()}
      >
        {/* Dynamic style overrides for high contrast accessibility mode */}
        <style>{highContrastStyles}</style>

        {/* Global Toast Notification System */}
        <AnimatePresence>
          {toast && (
            <motion.div 
              initial={{ opacity: 0, y: -20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              className={`fixed top-4 right-4 z-[9999] px-4 py-3 rounded-xl shadow-lg-custom border text-xs font-bold flex items-center gap-2 ${
                toast.type === 'success' ? 'bg-green-light text-green border-green/20' :
                toast.type === 'error' ? 'bg-red-light text-red border-red/20' : 'bg-teal-light text-teal border-teal-medium/20'
              }`}
            >
              {toast.type === 'success' ? '🏆' : toast.type === 'error' ? '🚨' : 'ℹ️'} {toast.message}
            </motion.div>
          )}
        </AnimatePresence>

        <Header 
          user={user} 
          onLogout={handleLogout} 
          lang={lang} 
          setLang={setLang} 
          demoMode={demoMode} 
          setDemoMode={setDemoMode} 
          showToast={showToast}
        />

        <div className="flex-1">
          <Routes>
            <Route
              path="/"
              element={user ? <UploadHome lang={lang} demoMode={demoMode} showToast={showToast} /> : <Login setUser={setUser} />}
            />
            <Route path="/login" element={<Login setUser={setUser} />} />
            <Route path="/register" element={<Register setUser={setUser} />} />
            <Route path="/analyze/:formId" element={user ? <Analyze lang={lang} showToast={showToast} /> : <Login setUser={setUser} />} />
            <Route path="/results/:formId" element={user ? <Results showToast={showToast} /> : <Login setUser={setUser} />} />
            <Route path="/dashboard" element={user ? <HistoryDashboard showToast={showToast} /> : <Login setUser={setUser} />} />
          </Routes>
        </div>

        {/* Floating Accessibility Widget */}
        <AccessibilityWidget accessibility={accessibility} setAccessibility={setAccessibility} />
      </div>
    </Router>
  );
}

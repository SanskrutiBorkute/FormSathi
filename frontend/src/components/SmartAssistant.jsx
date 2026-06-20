import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, Sparkles } from 'lucide-react';

export default function SmartAssistant({ formId, lang }) {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: lang === 'hi'
        ? "नमस्ते! मैं फॉर्मसाथी सहायक हूं। इस फॉर्म के बारे में मुझसे कुछ भी पूछें।"
        : lang === 'mr'
          ? "नमस्कार! मी फॉर्मसाथी सहाय्यक आहे. या अर्जाबद्दल मला काहीही विचारा."
          : "Hello! I am FormSaathi assistant. Ask me anything about this form."
    }
  ]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    // Scroll chat to bottom
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    const userText = query;
    setMessages(prev => [...prev, { sender: 'user', text: userText }]);
    setQuery('');
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`/api/forms/${formId}/chat`, {
        query: userText,
        lang: lang
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setMessages(prev => [...prev, { sender: 'ai', text: response.data.response }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { sender: 'ai', text: 'Sorry, I encountered an issue while communicating. Please check your network connection.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white border border-paper-darker rounded-xl flex flex-col h-[340px] shadow-sm-custom overflow-hidden">
      <div className="bg-teal text-white px-4 py-2.5 flex items-center gap-1.5 border-b border-teal-dark flex-shrink-0">
        <Sparkles className="w-4 h-4 text-saffron fill-current animate-pulse" />
        <span className="font-serif font-bold text-xs uppercase tracking-wider">Smart Form Assistant</span>
      </div>

      <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-2 bg-paper-light">
        {messages.map((msg, i) => (
          <div key={i} className={`flex items-start gap-2 max-w-[85%] ${msg.sender === 'user' ? 'self-end flex-row-reverse' : 'self-start'}`}>
            <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${msg.sender === 'user' ? 'bg-saffron text-white' : 'bg-teal text-white'}`}>
              {msg.sender === 'user' ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
            </div>
            <div className={`p-2.5 rounded-lg text-xs leading-relaxed ${msg.sender === 'user' ? 'bg-saffron-light text-ink border border-saffron-dark/10 rounded-tr-none' : 'bg-white text-ink border border-paper-darker rounded-tl-none'}`}>
              <p className="whitespace-pre-wrap">{msg.text}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-start gap-2 self-start max-w-[85%]">
            <div className="w-6 h-6 rounded-full bg-teal text-white flex items-center justify-center flex-shrink-0">
              <Bot className="w-3.5 h-3.5" />
            </div>
            <div className="p-2.5 rounded-lg text-xs bg-white text-ink-light border border-paper-darker rounded-tl-none animate-pulse">
              AI is writing...
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      <form onSubmit={handleSend} className="p-2 border-t border-paper-darker flex gap-1.5 bg-paper-dark flex-shrink-0">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={lang === 'hi' ? "प्रश्न पूछें..." : lang === 'mr' ? "प्रश्न विचारा..." : "Ask a question..."}
          className="flex-1 px-3 py-1.5 bg-white border border-paper-darker rounded-lg text-xs outline-none focus:border-teal font-sans"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="bg-teal text-white p-2 rounded-lg hover:bg-teal-dark transition-colors disabled:opacity-50 flex-shrink-0"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
}

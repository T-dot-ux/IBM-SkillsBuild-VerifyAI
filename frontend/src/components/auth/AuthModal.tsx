import { useState } from "react";
import { X, User as UserIcon, Key } from "lucide-react";
import { motion } from "framer-motion";

interface AuthModalProps {
  onClose: () => void;
  onSuccess: (token: string) => void;
}

export const AuthModal = ({ onClose, onSuccess }: AuthModalProps) => {
  const [username, setUsername] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch(`http://localhost:8000/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, gemini_api_key: apiKey })
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Invalid API Key or Server Error");
      }

      const data = await res.json();
      onSuccess(data.access_token);
      onClose();

    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <motion.div 
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        className="relative w-full max-w-md p-8 bg-white border-4 border-black rounded-2xl shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]"
      >
        <button onClick={onClose} className="absolute top-4 right-4 text-black hover:text-red-500 transition-colors">
          <X className="w-6 h-6" />
        </button>
        
        <h2 className="text-3xl font-black text-black mb-2 flex items-center gap-2 tracking-tight">
          VerifyAI
        </h2>
        <p className="text-black font-bold mb-6">Enter your name and Gemini API key to begin.</p>

        {error && (
          <motion.div 
            initial={{ opacity: 0, x: -10 }} 
            animate={{ opacity: 1, x: 0 }}
            className="mb-4 p-3 bg-red-400 border-2 border-black text-black font-bold text-sm rounded-lg"
          >
            {error}
          </motion.div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-black text-black mb-1 flex items-center gap-2">
              <UserIcon className="w-4 h-4 text-blue-500" /> NAME
            </label>
            <input 
              type="text" 
              required 
              placeholder="e.g. Alex"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full p-3 border-4 border-black rounded-xl text-black font-bold focus:border-blue-500 focus:outline-none transition-colors shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
            />
          </div>
          <div>
            <label className="block text-sm font-black text-black mb-1 flex items-center gap-2">
              <Key className="w-4 h-4 text-orange-500" /> GEMINI API KEY
            </label>
            <input 
              type="password"
              required
              placeholder="AIzaSy..." 
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-full p-3 border-4 border-black rounded-xl text-black font-bold focus:border-orange-500 focus:outline-none transition-colors shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
            />
            <p className="text-xs text-black font-bold mt-2 opacity-70">Your key is encrypted and strictly used for local verification.</p>
          </div>

          <motion.button 
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            type="submit" 
            disabled={loading}
            className="w-full py-4 mt-4 bg-green-400 text-black font-black text-xl rounded-xl border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:bg-green-500 transition-colors disabled:opacity-50"
          >
            {loading ? "VERIFYING..." : "ENTER MISSION CONTROL"}
          </motion.button>
        </form>
      </motion.div>
    </div>
  );
};

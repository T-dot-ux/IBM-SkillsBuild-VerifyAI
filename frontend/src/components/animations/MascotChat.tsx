import { useState, useEffect, useRef } from "react";
import { Mascot } from "./Mascot";
import { Mic, MicOff, Send, Loader2, Paperclip, AlertTriangle, CheckCircle, Info } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { verifyApi } from "@/lib/api";

interface ReasoningNode {
  agent: string;
  finding: string;
  impact: string;
}

interface Message {
  id: string;
  sender: "user" | "mascot";
  text: string;
  verification?: {
    filename: string;
    trustScore: number | null;
    status: string;
    verdict: string;
    summary: string;
    reasoning_tree: ReasoningNode[];
    trust_breakdown?: {
      threat_score: number;
      source_credibility: number;
      evidence_quality: number;
      technical_integrity: number;
    };
  };
}

export const MascotChat = () => {
  const [messages, setMessages] = useState<Message[]>([
    { id: "1", sender: "mascot", text: "Hello! I am your VerifyAI Copilot. You can ask me to verify a website, upload a document, or just chat with me! Speak in English or Hindi." }
  ]);
  const [input, setInput] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [mascotState, setMascotState] = useState<"idle" | "working" | "success" | "warning" | "error">("idle");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = false;
        
        recognitionRef.current.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setInput(transcript);
          handleSend(transcript);
        };
        
        recognitionRef.current.onerror = (event: any) => {
          console.error("Speech recognition error", event.error);
          setIsListening(false);
        };
        
        recognitionRef.current.onend = () => {
          setIsListening(false);
        };
      }
    }
  }, []);

  const toggleListen = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current?.start();
        setIsListening(true);
      } catch (e) {
        console.error("Speech API error:", e);
      }
    }
  };

  const handleSend = async (text: string) => {
    if (!text.trim()) return;
    
    const newMsg: Message = { id: Date.now().toString(), sender: "user", text };
    setMessages(prev => [...prev, newMsg]);
    setInput("");
    setMascotState("working");

    try {
      const token = localStorage.getItem("token");
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { "Authorization": `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ message: text })
      });

      if (!res.ok) throw new Error("Failed to communicate");
      
      const data = await res.json();
      
      setMascotState(data.risk_level === "HIGH" || data.risk_level === "CRITICAL" ? "error" : "success");
      
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        sender: "mascot",
        text: data.reply
      }]);
      
      setTimeout(() => setMascotState("idle"), 3000);
      
    } catch (err) {
      console.error(err);
      setMascotState("error");
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        sender: "mascot",
        text: "Sorry, my systems are currently offline or encountered an error."
      }]);
      setTimeout(() => setMascotState("idle"), 2000);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Render file upload message
    const userMsg: Message = { 
      id: Date.now().toString(), 
      sender: "user", 
      text: `Uploaded file: ${file.name}` 
    };
    setMessages(prev => [...prev, userMsg]);
    setMascotState("working");

    const mascotLoadingMsgId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, {
      id: mascotLoadingMsgId,
      sender: "mascot",
      text: `Analyzing ${file.name}... Please wait.`
    }]);

    try {
      // 1. Upload document
      const uploadRes = await verifyApi.uploadDocument(file);
      const jobId = uploadRes.job_id;

      // 2. Poll job status
      const pollInterval = setInterval(async () => {
        try {
          const statusRes = await verifyApi.getJobStatus(jobId);
          if (statusRes.status === "COMPLETED") {
            clearInterval(pollInterval);
            setMascotState(statusRes.trust_score < 50 ? "error" : "success");

            // Replace loading message with results card
            setMessages(prev => prev.map(m => m.id === mascotLoadingMsgId ? {
              id: mascotLoadingMsgId,
              sender: "mascot",
              text: `Analysis complete for ${file.name}!`,
              verification: {
                filename: file.name,
                trustScore: statusRes.trust_score,
                status: statusRes.trust_score < 50 ? "HIGH RISK" : statusRes.trust_score < 80 ? "MEDIUM RISK" : "LOW RISK",
                verdict: statusRes.recommendation,
                summary: statusRes.summary,
                reasoning_tree: statusRes.reasoning_tree || [],
                trust_breakdown: statusRes.trust_breakdown || undefined,
              }
            } : m));

            setTimeout(() => setMascotState("idle"), 3000);
          } else if (statusRes.status === "FAILED") {
            clearInterval(pollInterval);
            setMascotState("error");
            setMessages(prev => prev.map(m => m.id === mascotLoadingMsgId ? {
              id: mascotLoadingMsgId,
              sender: "mascot",
              text: `Analysis failed for ${file.name}.`
            } : m));
            setTimeout(() => setMascotState("idle"), 3000);
          }
        } catch (pollErr) {
          console.error("Polling error:", pollErr);
          clearInterval(pollInterval);
          setMascotState("error");
        }
      }, 1000);

    } catch (uploadErr: any) {
      console.error("Upload failed:", uploadErr);
      setMascotState("error");
      setMessages(prev => prev.map(m => m.id === mascotLoadingMsgId ? {
        id: mascotLoadingMsgId,
        sender: "mascot",
        text: `Failed to upload and analyze ${file.name}. Make sure your Gemini API key is valid.`
      } : m));
      setTimeout(() => setMascotState("idle"), 2000);
    }
  };

  return (
    <div className="flex flex-col md:flex-row gap-6 w-full max-w-5xl mx-auto items-end">
      {/* Mascot Side */}
      <div className="w-full md:w-1/3 flex flex-col items-center justify-center relative">
        <Mascot state={mascotState} />
      </div>

      {/* Chat Side */}
      <div className="w-full md:w-2/3 bg-white border-8 border-black rounded-3xl shadow-[16px_16px_0px_0px_rgba(0,0,0,1)] flex flex-col h-[520px] overflow-hidden">
        {/* Header */}
        <div className="bg-yellow-400 border-b-8 border-black p-4 flex justify-between items-center">
          <h3 className="text-xl font-black uppercase tracking-tight text-black">Copilot Link</h3>
          <div className="flex gap-2">
            <span className="w-3 h-3 rounded-full bg-red-500 border-2 border-black animate-pulse"></span>
            <span className="w-3 h-3 rounded-full bg-green-500 border-2 border-black"></span>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
          <AnimatePresence>
            {messages.map((m) => (
              <motion.div
                key={m.id}
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                className={`flex gap-3 ${m.sender === "user" ? "flex-row-reverse" : "flex-row"}`}
              >
                <div className={`w-10 h-10 rounded-full border-4 border-black flex-shrink-0 flex items-center justify-center ${m.sender === "user" ? "bg-blue-500" : "bg-green-400"}`}>
                  {m.sender === "user" ? "👤" : "🤖"}
                </div>
                
                <div className="flex flex-col gap-2 max-w-[85%]">
                  <div className={`p-3 rounded-2xl border-4 border-black font-bold text-black ${m.sender === "user" ? "bg-white rounded-tr-none" : "bg-yellow-100 rounded-tl-none"}`}>
                    {m.text}
                  </div>

                  {/* Render Verification Card if present */}
                  {m.verification && (
                    <motion.div 
                      initial={{ scale: 0.9, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      className="border-4 border-black rounded-2xl p-4 bg-white shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] flex flex-col gap-3 text-black"
                    >
                      <div className="flex justify-between items-center border-b-4 border-black pb-2">
                        <span className="font-black text-sm uppercase tracking-wider">{m.verification.filename}</span>
                        <span className={`px-3 py-0.5 rounded-full border-2 border-black font-black text-xs ${
                          m.verification.status === "HIGH RISK" ? "bg-red-400" :
                          m.verification.status === "MEDIUM RISK" ? "bg-yellow-400" : "bg-green-400"
                        }`}>
                          {m.verification.status}
                        </span>
                      </div>
                      
                      <div className="flex items-center gap-4 py-2">
                        {/* Interactive score counter */}
                        <div className="text-center bg-black text-white p-3 rounded-xl border-2 border-black flex flex-col justify-center min-w-[70px]">
                          <span className="text-3xl font-black">{m.verification.trustScore}</span>
                          <span className="text-xs font-bold text-gray-400">/100</span>
                        </div>
                        
                        <div className="flex-1">
                          <p className="font-black text-sm uppercase text-gray-700">Verdict</p>
                          <p className="font-bold text-sm leading-snug">{m.verification.verdict}</p>
                        </div>
                      </div>

                      {/* Trust Breakdown Bars */}
                      {m.verification.trust_breakdown && (
                        <div className="bg-gray-50 p-3 rounded-xl border-2 border-black space-y-2">
                          <span className="uppercase text-gray-600 block mb-2 text-xs font-black">Trust Breakdown</span>
                          {Object.entries(m.verification.trust_breakdown).map(([key, val]) => (
                            <div key={key} className="flex items-center gap-2 text-xs">
                              <span className="w-28 font-bold text-gray-700 capitalize">{key.replace(/_/g, " ")}</span>
                              <div className="flex-1 bg-gray-200 rounded-full h-3 border border-black overflow-hidden">
                                <div
                                  className={`h-full rounded-full ${val >= 70 ? "bg-green-400" : val >= 40 ? "bg-yellow-400" : "bg-red-400"}`}
                                  style={{ width: `${val}%` }}
                                />
                              </div>
                              <span className="font-black w-8 text-right">{val}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Reasoning Tree */}
                      {m.verification.reasoning_tree && m.verification.reasoning_tree.length > 0 ? (
                        <div className="bg-gray-100 p-3 rounded-xl border-2 border-black space-y-2 max-h-60 overflow-y-auto">
                          <span className="uppercase text-gray-600 block mb-1 text-xs font-black">Reasoning Chain</span>
                          {m.verification.reasoning_tree.map((node, idx) => (
                            <div key={idx} className={`flex gap-2 items-start p-2 rounded-lg border-2 text-xs ${
                              node.impact === "CRITICAL" ? "bg-red-100 border-red-400" :
                              node.impact === "HIGH" ? "bg-orange-100 border-orange-400" :
                              node.impact === "MODERATE" ? "bg-yellow-100 border-yellow-400" :
                              "bg-green-100 border-green-400"
                            }`}>
                              <div className="flex-shrink-0 mt-0.5">
                                {node.impact === "CRITICAL" || node.impact === "HIGH" ? (
                                  <AlertTriangle className="w-3.5 h-3.5 text-red-600" />
                                ) : node.impact === "MODERATE" ? (
                                  <AlertTriangle className="w-3.5 h-3.5 text-yellow-600" />
                                ) : (
                                  <CheckCircle className="w-3.5 h-3.5 text-green-600" />
                                )}
                              </div>
                              <div>
                                <span className="font-black uppercase text-[10px] text-gray-500 block">{node.agent}</span>
                                <span className="font-bold leading-snug">{node.finding}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="bg-gray-100 p-2.5 rounded-xl border-2 border-black text-xs font-bold leading-normal">
                          <span className="uppercase text-gray-600 block mb-1">Reasoning Chain</span>
                          {m.verification.summary}
                        </div>
                      )}
                    </motion.div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 bg-white border-t-8 border-black flex gap-2">
          {/* File Upload Button */}
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileUpload} 
            className="hidden" 
            accept=".pdf,.png,.jpg,.jpeg"
          />
          <button 
            onClick={() => fileInputRef.current?.click()}
            disabled={mascotState === "working"}
            className="p-3 bg-yellow-300 rounded-xl border-4 border-black hover:bg-yellow-400 disabled:opacity-50 transition-colors"
          >
            <Paperclip className="w-6 h-6 text-black" />
          </button>

          <button 
            onClick={toggleListen}
            className={`p-3 rounded-xl border-4 border-black transition-colors ${isListening ? "bg-red-500 text-white animate-pulse" : "bg-pink-400 text-black hover:bg-pink-500"}`}
          >
            {isListening ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
          </button>
          
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend(input)}
            placeholder="Type or speak a link..."
            className="flex-1 p-3 border-4 border-black rounded-xl font-bold text-black focus:outline-none focus:border-blue-500"
          />
          
          <button 
            onClick={() => handleSend(input)}
            disabled={mascotState === "working" || !input.trim()}
            className="p-3 bg-blue-500 text-white rounded-xl border-4 border-black hover:bg-blue-600 disabled:opacity-50 transition-colors"
          >
            {mascotState === "working" ? <Loader2 className="w-6 h-6 animate-spin" /> : <Send className="w-6 h-6" />}
          </button>
        </div>
      </div>
    </div>
  );
};

"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { UploadCloud, FileType, CheckCircle } from "lucide-react";

export const UploadZone = ({ onUpload }: { onUpload: (file: File) => void }) => {
  const [file, setFile] = useState<File | null>(null);

  const onDrop = useCallback((acceptedFiles: File[], fileRejections: any[]) => {
    if (fileRejections.length > 0) {
      alert("Invalid file type. Please upload a .png, .jpg, .jpeg, .pdf, .docx, or .txt file.");
      return;
    }
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      // Trigger ripple/success animation, then call onUpload
      setTimeout(() => {
        onUpload(acceptedFiles[0]);
      }, 1500);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxFiles: 1,
    accept: {
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    }
  });

  return (
    <div className="w-full max-w-2xl mx-auto">
      <motion.div
        {...(getRootProps() as any)}
        animate={{
          scale: isDragActive ? 1.02 : 1,
          borderColor: isDragActive ? "#00ffff" : "rgba(255,255,255,0.2)",
          boxShadow: isDragActive ? "0 0 40px rgba(0,255,255,0.2)" : "0 0 0px rgba(0,0,0,0)",
        }}
        whileHover={{
          scale: 1.01,
          borderColor: "rgba(0,102,255,0.5)",
          boxShadow: "0 0 20px rgba(0,102,255,0.15)",
        }}
        className="relative cursor-pointer overflow-hidden rounded-3xl border-2 border-dashed bg-white/5 backdrop-blur-md p-16 flex flex-col items-center justify-center transition-colors group"
      >
        <input {...getInputProps()} />
        
        {/* Glow effect in background */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-secondary/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        
        <AnimatePresence mode="wait">
          {!file ? (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex flex-col items-center z-10"
            >
              <motion.div
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
              >
                <UploadCloud className="w-20 h-20 text-primary mb-6 drop-shadow-[0_0_15px_rgba(0,102,255,0.5)]" />
              </motion.div>
              <h3 className="text-2xl font-bold text-white mb-2">Upload your file</h3>
              <p className="text-slate-400 text-center max-w-sm">
                Drag and drop your document, screenshot, or pdf here, or click to browse.
              </p>
            </motion.div>
          ) : (
            <motion.div
              key="success"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="flex flex-col items-center z-10"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 0.5 }}
                className="relative"
              >
                <motion.div 
                  animate={{ scale: [1, 2, 1], opacity: [0.5, 0, 0.5] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  className="absolute inset-0 bg-emerald-500 rounded-full blur-xl"
                />
                <CheckCircle className="w-20 h-20 text-emerald-400 relative z-10 drop-shadow-[0_0_15px_rgba(16,185,129,0.8)]" />
              </motion.div>
              <h3 className="text-xl font-bold text-white mb-2 mt-6">{file.name}</h3>
              <motion.p 
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="text-emerald-400 font-medium tracking-wide"
              >
                Scanning with VerifyAI Agents...
              </motion.p>
              
              {/* Ripple Ring */}
              <motion.div
                initial={{ scale: 1, opacity: 0.5 }}
                animate={{ scale: 3, opacity: 0 }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "easeOut" }}
                className="absolute w-32 h-32 border-2 border-emerald-500 rounded-full"
              />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

import React, { useCallback } from 'react';
import { Upload, Image, X, FileImage } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from 'framer-motion';

export default function ImageUploader({ images, setImages, isProcessing }) {
  const handleFileChange = useCallback((e) => {
    const files = Array.from(e.target.files);
    const validFiles = files.filter(file => 
      file.type.startsWith('image/')
    );
    
    validFiles.forEach(file => {
      const reader = new FileReader();
      reader.onload = (event) => {
        setImages(prev => [...prev, {
          file,
          preview: event.target.result,
          name: file.name,
          id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        }]);
      };
      reader.readAsDataURL(file);
    });
  }, [setImages]);

  const removeImage = (id) => {
    setImages(prev => prev.filter(img => img.id !== id));
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    const validFiles = files.filter(file => file.type.startsWith('image/'));
    
    validFiles.forEach(file => {
      const reader = new FileReader();
      reader.onload = (event) => {
        setImages(prev => [...prev, {
          file,
          preview: event.target.result,
          name: file.name,
          id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        }]);
      };
      reader.readAsDataURL(file);
    });
  }, [setImages]);

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  return (
    <div className="space-y-6">
      {/* Zone de drop */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className="relative border-2 border-dashed border-slate-200 rounded-2xl p-12 text-center 
                   hover:border-violet-400 hover:bg-violet-50/30 transition-all duration-300 cursor-pointer
                   group"
      >
        <input
          type="file"
          multiple
          accept="image/*"
          onChange={handleFileChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={isProcessing}
        />
        
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-100 to-indigo-100 
                          flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
            <Upload className="w-8 h-8 text-violet-600" />
          </div>
          <div>
            <p className="text-lg font-medium text-slate-700">
              Glissez vos captures d'écran ici
            </p>
            <p className="text-sm text-slate-500 mt-1">
              ou cliquez pour sélectionner • JPG, PNG, JPEG
            </p>
          </div>
        </div>
      </div>

      {/* Prévisualisation des images */}
      <AnimatePresence>
        {images.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-3"
          >
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-slate-600">
                {images.length} image{images.length > 1 ? 's' : ''} sélectionnée{images.length > 1 ? 's' : ''}
              </h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setImages([])}
                className="text-slate-500 hover:text-red-500"
                disabled={isProcessing}
              >
                Tout supprimer
              </Button>
            </div>
            
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {images.map((img) => (
                <motion.div
                  key={img.id}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="relative group aspect-square rounded-xl overflow-hidden bg-slate-100"
                >
                  <img
                    src={img.preview}
                    alt={img.name}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent 
                                  opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                  <button
                    onClick={() => removeImage(img.id)}
                    disabled={isProcessing}
                    className="absolute top-2 right-2 w-7 h-7 rounded-full bg-white/90 
                               flex items-center justify-center opacity-0 group-hover:opacity-100 
                               transition-opacity duration-200 hover:bg-red-500 hover:text-white"
                  >
                    <X className="w-4 h-4" />
                  </button>
                  <p className="absolute bottom-2 left-2 right-2 text-xs text-white truncate 
                                opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                    {img.name}
                  </p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

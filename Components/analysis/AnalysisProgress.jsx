import React from 'react';
import { Loader2, CheckCircle2, Image, MessageSquare, Brain } from 'lucide-react';
import { Progress } from "@/components/ui/progress";
import { motion } from 'framer-motion';

export default function AnalysisProgress({ 
  currentStep, 
  currentImage, 
  totalImages,
  commentsExtracted,
  commentsAnalyzed
}) {
  const steps = [
    { id: 'upload', label: 'Upload des images', icon: Image },
    { id: 'extract', label: 'Extraction des commentaires', icon: MessageSquare },
    { id: 'analyze', label: 'Analyse des sentiments', icon: Brain },
  ];

  const getStepStatus = (stepId) => {
    const stepOrder = ['upload', 'extract', 'analyze'];
    const currentIndex = stepOrder.indexOf(currentStep);
    const stepIndex = stepOrder.indexOf(stepId);
    
    if (stepIndex < currentIndex) return 'completed';
    if (stepIndex === currentIndex) return 'active';
    return 'pending';
  };

  const progress = totalImages > 0 
    ? Math.round((currentImage / totalImages) * 100) 
    : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl border border-slate-200 p-8 space-y-8"
    >
      {/* Étapes */}
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const status = getStepStatus(step.id);
          const Icon = step.icon;
          
          return (
            <React.Fragment key={step.id}>
              <div className="flex items-center gap-3">
                <div className={`
                  w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300
                  ${status === 'completed' ? 'bg-green-100 text-green-600' : ''}
                  ${status === 'active' ? 'bg-violet-100 text-violet-600' : ''}
                  ${status === 'pending' ? 'bg-slate-100 text-slate-400' : ''}
                `}>
                  {status === 'completed' ? (
                    <CheckCircle2 className="w-5 h-5" />
                  ) : status === 'active' ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Icon className="w-5 h-5" />
                  )}
                </div>
                <span className={`
                  text-sm font-medium hidden sm:block
                  ${status === 'active' ? 'text-violet-700' : ''}
                  ${status === 'completed' ? 'text-green-700' : ''}
                  ${status === 'pending' ? 'text-slate-400' : ''}
                `}>
                  {step.label}
                </span>
              </div>
              
              {index < steps.length - 1 && (
                <div className={`
                  flex-1 h-0.5 mx-4 rounded-full transition-colors duration-300
                  ${getStepStatus(steps[index + 1].id) !== 'pending' ? 'bg-violet-200' : 'bg-slate-200'}
                `} />
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Progression détaillée */}
      <div className="space-y-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-600">
            Image {currentImage} / {totalImages}
          </span>
          <span className="font-medium text-violet-600">{progress}%</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      {/* Statistiques en temps réel */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-slate-50 rounded-xl p-4">
          <p className="text-2xl font-bold text-slate-800">{commentsExtracted}</p>
          <p className="text-sm text-slate-500">Commentaires extraits</p>
        </div>
        <div className="bg-slate-50 rounded-xl p-4">
          <p className="text-2xl font-bold text-slate-800">{commentsAnalyzed}</p>
          <p className="text-sm text-slate-500">Commentaires analysés</p>
        </div>
      </div>
    </motion.div>
  );
}

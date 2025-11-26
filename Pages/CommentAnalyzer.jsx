import React, { useState } from 'react';
import { base44 } from '@/api/base44Client';
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Play, Download, RotateCcw, FileSpreadsheet, 
  BarChart3, Table, Sparkles, AlertCircle
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

import ImageUploader from '@/components/analysis/ImageUploader';
import AnalysisProgress from '@/components/analysis/AnalysisProgress';
import ResultsTable from '@/components/analysis/ResultsTable';
import StatsDashboard from '@/components/analysis/StatsDashboard';

export default function CommentAnalyzer() {
  const [images, setImages] = useState([]);
  const [results, setResults] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(null);
  const [progress, setProgress] = useState({ 
    currentImage: 0, 
    totalImages: 0,
    commentsExtracted: 0,
    commentsAnalyzed: 0
  });
  const [activeTab, setActiveTab] = useState('upload');

  const extractCommentsFromImage = async (imageFile) => {
    const { file_url } = await base44.integrations.Core.UploadFile({ file: imageFile });
    
    const response = await base44.integrations.Core.InvokeLLM({
      prompt: `Extrais tous les commentaires utilisateurs visibles dans cette capture d'écran.

Règles:
- Inclure uniquement le texte des commentaires, pas les noms d'utilisateurs, dates ou éléments d'interface
- Chaque commentaire doit être une chaîne séparée
- Préserver le texte original exactement comme écrit
- Ignorer les commentaires vides ou dupliqués

Retourne un objet JSON avec une clé "comments" contenant un tableau de chaînes.`,
      file_urls: [file_url],
      response_json_schema: {
        type: "object",
        properties: {
          comments: {
            type: "array",
            items: { type: "string" }
          }
        },
        required: ["comments"]
      }
    });

    return response.comments || [];
  };

  const analyzeComment = async (comment) => {
    const response = await base44.integrations.Core.InvokeLLM({
      prompt: `Analyse ce commentaire utilisateur et détermine:
1. Le sentiment (positive, neutral, ou negative)
2. Un score de confiance entre 0 et 1
3. Le topic (sujet spécifique)
4. Le thème (catégorie générale)

Commentaire: "${comment}"

Réponds en JSON.`,
      response_json_schema: {
        type: "object",
        properties: {
          sentiment: { 
            type: "string", 
            enum: ["positive", "neutral", "negative"] 
          },
          confidence: { type: "number" },
          topic: { type: "string" },
          theme: { type: "string" }
        },
        required: ["sentiment", "confidence", "topic", "theme"]
      }
    });

    return response;
  };

  const startAnalysis = async () => {
    if (images.length === 0) {
      toast.error("Veuillez ajouter au moins une image");
      return;
    }

    setIsProcessing(true);
    setResults([]);
    setProgress({ 
      currentImage: 0, 
      totalImages: images.length,
      commentsExtracted: 0,
      commentsAnalyzed: 0
    });

    const batchId = `batch-${Date.now()}`;
    const allResults = [];

    try {
      // Étape 1: Upload et extraction
      setCurrentStep('extract');
      
      for (let i = 0; i < images.length; i++) {
        const img = images[i];
        setProgress(prev => ({ ...prev, currentImage: i + 1 }));

        try {
          const comments = await extractCommentsFromImage(img.file);
          setProgress(prev => ({ 
            ...prev, 
            commentsExtracted: prev.commentsExtracted + comments.length 
          }));

          // Étape 2: Analyse de chaque commentaire
          setCurrentStep('analyze');
          
          for (const comment of comments) {
            if (!comment.trim() || comment.length < 10) continue;

            try {
              const analysis = await analyzeComment(comment);
              
              const result = {
                image_source: img.name,
                comment: comment,
                sentiment: analysis.sentiment,
                confidence: analysis.confidence,
                topic: analysis.topic,
                theme: analysis.theme,
                batch_id: batchId
              };

              allResults.push(result);
              setResults([...allResults]);
              setProgress(prev => ({ 
                ...prev, 
                commentsAnalyzed: prev.commentsAnalyzed + 1 
              }));

              // Sauvegarder dans la base
              await base44.entities.CommentAnalysis.create(result);
            } catch (err) {
              console.error('Erreur analyse commentaire:', err);
            }
          }
        } catch (err) {
          console.error(`Erreur traitement image ${img.name}:`, err);
          toast.error(`Erreur sur ${img.name}`);
        }
      }

      toast.success(`Analyse terminée: ${allResults.length} commentaires analysés`);
      setActiveTab('results');
    } catch (error) {
      console.error('Erreur analyse:', error);
      toast.error("Une erreur est survenue pendant l'analyse");
    } finally {
      setIsProcessing(false);
      setCurrentStep(null);
    }
  };

  const exportToCSV = () => {
    if (results.length === 0) return;

    const headers = ['image_source', 'comment', 'sentiment', 'confidence', 'topic', 'theme'];
    const csvContent = [
      headers.join(','),
      ...results.map(row => 
        headers.map(h => `"${(row[h] || '').toString().replace(/"/g, '""')}"`).join(',')
      )
    ].join('\n');

    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `comments_analysis_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    
    toast.success('Export CSV téléchargé');
  };

  const resetAll = () => {
    setImages([]);
    setResults([]);
    setProgress({ currentImage: 0, totalImages: 0, commentsExtracted: 0, commentsAnalyzed: 0 });
    setActiveTab('upload');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-violet-50/30">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-slate-200/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 
                              flex items-center justify-center shadow-lg shadow-violet-500/25">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-800">
                  Analyseur de Commentaires
                </h1>
                <p className="text-sm text-slate-500">
                  Extraction & analyse de sentiments par IA
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {results.length > 0 && (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={exportToCSV}
                    className="gap-2"
                  >
                    <Download className="w-4 h-4" />
                    Export CSV
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={resetAll}
                    className="gap-2 text-slate-500"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Réinitialiser
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-slate-100/80 p-1 mb-8">
            <TabsTrigger value="upload" className="gap-2">
              <FileSpreadsheet className="w-4 h-4" />
              Import
            </TabsTrigger>
            <TabsTrigger value="results" disabled={results.length === 0} className="gap-2">
              <Table className="w-4 h-4" />
              Résultats ({results.length})
            </TabsTrigger>
            <TabsTrigger value="stats" disabled={results.length === 0} className="gap-2">
              <BarChart3 className="w-4 h-4" />
              Statistiques
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upload" className="space-y-8">
            {/* Zone d'upload */}
            <div className="bg-white rounded-2xl border border-slate-200 p-8">
              <ImageUploader 
                images={images} 
                setImages={setImages}
                isProcessing={isProcessing}
              />
            </div>

            {/* Progression */}
            <AnimatePresence>
              {isProcessing && (
                <AnalysisProgress
                  currentStep={currentStep}
                  currentImage={progress.currentImage}
                  totalImages={progress.totalImages}
                  commentsExtracted={progress.commentsExtracted}
                  commentsAnalyzed={progress.commentsAnalyzed}
                />
              )}
            </AnimatePresence>

            {/* Bouton de lancement */}
            {!isProcessing && images.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-center"
              >
                <Button
                  size="lg"
                  onClick={startAnalysis}
                  className="gap-3 bg-gradient-to-r from-violet-600 to-indigo-600 
                             hover:from-violet-700 hover:to-indigo-700 
                             shadow-lg shadow-violet-500/25 px-8"
                >
                  <Play className="w-5 h-5" />
                  Lancer l'analyse
                </Button>
              </motion.div>
            )}

            {/* Info box */}
            {!isProcessing && images.length === 0 && (
              <div className="bg-violet-50 rounded-2xl p-6 flex items-start gap-4">
                <div className="w-10 h-10 rounded-xl bg-violet-100 flex items-center justify-center flex-shrink-0">
                  <AlertCircle className="w-5 h-5 text-violet-600" />
                </div>
                <div>
                  <h3 className="font-medium text-violet-900">Comment ça marche ?</h3>
                  <p className="text-sm text-violet-700 mt-1">
                    1. Uploadez vos captures d'écran contenant des commentaires<br />
                    2. L'IA extrait automatiquement les textes des commentaires<br />
                    3. Chaque commentaire est analysé pour son sentiment, topic et thème<br />
                    4. Visualisez les résultats et exportez en CSV
                  </p>
                </div>
              </div>
            )}
          </TabsContent>

          <TabsContent value="results">
            <ResultsTable results={results} />
          </TabsContent>

          <TabsContent value="stats">
            <StatsDashboard results={results} />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

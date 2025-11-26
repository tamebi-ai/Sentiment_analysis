import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  PieChart, Pie, Cell, ResponsiveContainer, 
  BarChart, Bar, XAxis, YAxis, Tooltip, 
  LineChart, Line, CartesianGrid
} from 'recharts';
import { TrendingUp, TrendingDown, Minus, MessageSquare, Image, Target, Layers } from 'lucide-react';
import { motion } from 'framer-motion';

const SENTIMENT_COLORS = {
  positive: '#10b981',
  neutral: '#64748b',
  negative: '#f43f5e'
};

export default function StatsDashboard({ results }) {
  // Calculs des statistiques
  const totalComments = results.length;
  const sentimentCounts = results.reduce((acc, item) => {
    acc[item.sentiment] = (acc[item.sentiment] || 0) + 1;
    return acc;
  }, {});

  const sentimentData = [
    { name: 'Positif', value: sentimentCounts.positive || 0, color: SENTIMENT_COLORS.positive },
    { name: 'Neutre', value: sentimentCounts.neutral || 0, color: SENTIMENT_COLORS.neutral },
    { name: 'Négatif', value: sentimentCounts.negative || 0, color: SENTIMENT_COLORS.negative },
  ];

  // Top thèmes
  const themeCounts = results.reduce((acc, item) => {
    if (item.theme) {
      acc[item.theme] = (acc[item.theme] || 0) + 1;
    }
    return acc;
  }, {});
  
  const themeData = Object.entries(themeCounts)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 6)
    .map(([name, value]) => ({ name, value }));

  // Top topics
  const topicCounts = results.reduce((acc, item) => {
    if (item.topic) {
      acc[item.topic] = (acc[item.topic] || 0) + 1;
    }
    return acc;
  }, {});
  
  const topicData = Object.entries(topicCounts)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 8)
    .map(([name, value]) => ({ name, value }));

  // Confiance moyenne
  const avgConfidence = results.length > 0
    ? results.reduce((sum, r) => sum + (r.confidence || 0), 0) / results.length
    : 0;

  // Images sources
  const uniqueImages = [...new Set(results.map(r => r.image_source).filter(Boolean))].length;

  // Sentiment dominant
  const dominantSentiment = Object.entries(sentimentCounts)
    .sort(([,a], [,b]) => b - a)[0];

  const StatCard = ({ title, value, subtitle, icon: Icon, trend, color = 'violet' }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl border border-slate-200 p-6"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-500">{title}</p>
          <p className="text-3xl font-bold text-slate-800 mt-1">{value}</p>
          {subtitle && (
            <p className="text-sm text-slate-400 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`w-12 h-12 rounded-xl bg-${color}-100 flex items-center justify-center`}>
          <Icon className={`w-6 h-6 text-${color}-600`} />
        </div>
      </div>
      {trend && (
        <div className="flex items-center gap-1 mt-4 text-sm">
          {trend === 'up' && <TrendingUp className="w-4 h-4 text-emerald-500" />}
          {trend === 'down' && <TrendingDown className="w-4 h-4 text-rose-500" />}
          {trend === 'neutral' && <Minus className="w-4 h-4 text-slate-400" />}
        </div>
      )}
    </motion.div>
  );

  return (
    <div className="space-y-6">
      {/* Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total commentaires"
          value={totalComments}
          icon={MessageSquare}
        />
        <StatCard
          title="Images analysées"
          value={uniqueImages}
          icon={Image}
        />
        <StatCard
          title="Confiance moyenne"
          value={`${Math.round(avgConfidence * 100)}%`}
          icon={Target}
        />
        <StatCard
          title="Thèmes détectés"
          value={Object.keys(themeCounts).length}
          icon={Layers}
        />
      </div>

      {/* Graphiques */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribution des sentiments */}
        <Card className="border-slate-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-semibold text-slate-800">
              Distribution des sentiments
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value) => [`${value} commentaires`, '']}
                    contentStyle={{ 
                      borderRadius: '12px', 
                      border: '1px solid #e2e8f0',
                      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-6 mt-4">
              {sentimentData.map((item) => (
                <div key={item.name} className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-sm text-slate-600">
                    {item.name} ({item.value})
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Top thèmes */}
        <Card className="border-slate-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-semibold text-slate-800">
              Top thèmes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={themeData} layout="vertical" margin={{ left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                  <XAxis type="number" tick={{ fontSize: 12, fill: '#64748b' }} />
                  <YAxis 
                    type="category" 
                    dataKey="name" 
                    width={120}
                    tick={{ fontSize: 12, fill: '#64748b' }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      borderRadius: '12px', 
                      border: '1px solid #e2e8f0'
                    }}
                  />
                  <Bar 
                    dataKey="value" 
                    fill="#8b5cf6" 
                    radius={[0, 6, 6, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top topics */}
      <Card className="border-slate-200">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg font-semibold text-slate-800">
            Top sujets détectés
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topicData} margin={{ bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis 
                  dataKey="name" 
                  tick={{ fontSize: 11, fill: '#64748b' }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis tick={{ fontSize: 12, fill: '#64748b' }} />
                <Tooltip 
                  contentStyle={{ 
                    borderRadius: '12px', 
                    border: '1px solid #e2e8f0'
                  }}
                />
                <Bar 
                  dataKey="value" 
                  fill="#6366f1" 
                  radius={[6, 6, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Matrice sentiment / thème */}
      {themeData.length > 0 && (
        <Card className="border-slate-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-semibold text-slate-800">
              Sentiments par thème
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200">
                    <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">Thème</th>
                    <th className="text-center py-3 px-4 text-sm font-medium text-emerald-600">Positif</th>
                    <th className="text-center py-3 px-4 text-sm font-medium text-slate-600">Neutre</th>
                    <th className="text-center py-3 px-4 text-sm font-medium text-rose-600">Négatif</th>
                    <th className="text-center py-3 px-4 text-sm font-medium text-slate-600">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {themeData.map((theme) => {
                    const themeResults = results.filter(r => r.theme === theme.name);
                    const pos = themeResults.filter(r => r.sentiment === 'positive').length;
                    const neu = themeResults.filter(r => r.sentiment === 'neutral').length;
                    const neg = themeResults.filter(r => r.sentiment === 'negative').length;
                    
                    return (
                      <tr key={theme.name} className="border-b border-slate-100 hover:bg-slate-50/50">
                        <td className="py-3 px-4 text-sm text-slate-700">{theme.name}</td>
                        <td className="text-center py-3 px-4">
                          <span className="inline-flex items-center justify-center w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 text-sm font-medium">
                            {pos}
                          </span>
                        </td>
                        <td className="text-center py-3 px-4">
                          <span className="inline-flex items-center justify-center w-8 h-8 rounded-lg bg-slate-100 text-slate-700 text-sm font-medium">
                            {neu}
                          </span>
                        </td>
                        <td className="text-center py-3 px-4">
                          <span className="inline-flex items-center justify-center w-8 h-8 rounded-lg bg-rose-50 text-rose-700 text-sm font-medium">
                            {neg}
                          </span>
                        </td>
                        <td className="text-center py-3 px-4 text-sm font-medium text-slate-800">
                          {theme.value}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

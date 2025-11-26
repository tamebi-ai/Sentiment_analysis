import React, { useState } from 'react';
import { 
  Table, TableBody, TableCell, TableHead, 
  TableHeader, TableRow 
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search, Filter, ChevronLeft, ChevronRight, Image } from 'lucide-react';
import { motion } from 'framer-motion';

const sentimentConfig = {
  positive: { 
    label: 'Positif', 
    className: 'bg-emerald-50 text-emerald-700 border-emerald-200' 
  },
  neutral: { 
    label: 'Neutre', 
    className: 'bg-slate-50 text-slate-700 border-slate-200' 
  },
  negative: { 
    label: 'Négatif', 
    className: 'bg-rose-50 text-rose-700 border-rose-200' 
  },
};

export default function ResultsTable({ results }) {
  const [search, setSearch] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState('all');
  const [themeFilter, setThemeFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Filtrage
  const filteredResults = results.filter(item => {
    const matchesSearch = item.comment.toLowerCase().includes(search.toLowerCase()) ||
                          item.topic?.toLowerCase().includes(search.toLowerCase()) ||
                          item.theme?.toLowerCase().includes(search.toLowerCase());
    const matchesSentiment = sentimentFilter === 'all' || item.sentiment === sentimentFilter;
    const matchesTheme = themeFilter === 'all' || item.theme === themeFilter;
    return matchesSearch && matchesSentiment && matchesTheme;
  });

  // Pagination
  const totalPages = Math.ceil(filteredResults.length / itemsPerPage);
  const paginatedResults = filteredResults.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Thèmes uniques pour le filtre
  const uniqueThemes = [...new Set(results.map(r => r.theme).filter(Boolean))];

  return (
    <div className="space-y-6">
      {/* Filtres */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            placeholder="Rechercher dans les commentaires..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setCurrentPage(1); }}
            className="pl-10"
          />
        </div>
        
        <Select value={sentimentFilter} onValueChange={(v) => { setSentimentFilter(v); setCurrentPage(1); }}>
          <SelectTrigger className="w-full sm:w-40">
            <SelectValue placeholder="Sentiment" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous les sentiments</SelectItem>
            <SelectItem value="positive">Positif</SelectItem>
            <SelectItem value="neutral">Neutre</SelectItem>
            <SelectItem value="negative">Négatif</SelectItem>
          </SelectContent>
        </Select>

        <Select value={themeFilter} onValueChange={(v) => { setThemeFilter(v); setCurrentPage(1); }}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="Thème" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous les thèmes</SelectItem>
            {uniqueThemes.map(theme => (
              <SelectItem key={theme} value={theme}>{theme}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Tableau */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="bg-slate-50/50">
                <TableHead className="w-12">#</TableHead>
                <TableHead className="min-w-[300px]">Commentaire</TableHead>
                <TableHead className="w-28">Sentiment</TableHead>
                <TableHead className="w-20">Confiance</TableHead>
                <TableHead className="w-40">Topic</TableHead>
                <TableHead className="w-40">Thème</TableHead>
                <TableHead className="w-32">Source</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginatedResults.map((item, idx) => (
                <motion.tr
                  key={item.id || idx}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: idx * 0.03 }}
                  className="group hover:bg-slate-50/50 transition-colors"
                >
                  <TableCell className="text-slate-400 text-sm">
                    {(currentPage - 1) * itemsPerPage + idx + 1}
                  </TableCell>
                  <TableCell>
                    <p className="text-sm text-slate-700 line-clamp-2">
                      {item.comment}
                    </p>
                  </TableCell>
                  <TableCell>
                    <Badge 
                      variant="outline" 
                      className={sentimentConfig[item.sentiment]?.className}
                    >
                      {sentimentConfig[item.sentiment]?.label || item.sentiment}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className="w-12 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-violet-500 rounded-full transition-all"
                          style={{ width: `${(item.confidence || 0) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-slate-500">
                        {Math.round((item.confidence || 0) * 100)}%
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <span className="text-sm text-slate-600">{item.topic || '-'}</span>
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary" className="bg-slate-100 text-slate-600 font-normal">
                      {item.theme || '-'}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1.5 text-xs text-slate-500">
                      <Image className="w-3.5 h-3.5" />
                      <span className="truncate max-w-[80px]">{item.image_source || '-'}</span>
                    </div>
                  </TableCell>
                </motion.tr>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-6 py-4 border-t border-slate-100">
            <p className="text-sm text-slate-500">
              {filteredResults.length} résultat{filteredResults.length > 1 ? 's' : ''}
            </p>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <span className="text-sm text-slate-600 px-2">
                {currentPage} / {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

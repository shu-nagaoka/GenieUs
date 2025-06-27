'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  IoLinkOutline,
  IoTimeOutline,
  IoSearchOutline,
  IoGlobeOutline,
  IoCheckmarkCircleOutline,
  IoInformationCircleOutline
} from 'react-icons/io5'

interface SearchResult {
  title: string
  url: string
  snippet: string
  displayLink?: string
  position?: number
}

interface SearchQuery {
  query: string
  timestamp: number
  results_count?: number
}

interface SearchResultsDisplayProps {
  searchQuery?: SearchQuery
  searchResults?: SearchResult[]
  isSearching?: boolean
  className?: string
}

export function SearchResultsDisplay({
  searchQuery,
  searchResults = [],
  isSearching = false,
  className = ""
}: SearchResultsDisplayProps) {
  
  // 検索中の場合の表示
  if (isSearching) {
    return (
      <Card className={`bg-blue-50/80 border-blue-200 ${className}`}>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent" />
            <CardTitle className="text-sm font-medium text-blue-700">
              🔍 最新情報を検索中...
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-sm text-blue-600">
            <IoSearchOutline className="h-4 w-4" />
            <span>Web検索を実行しています</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  // 検索クエリと結果がない場合は何も表示しない
  if (!searchQuery && (!searchResults || searchResults.length === 0)) {
    return null
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {/* 検索クエリ情報表示 */}
      {searchQuery && (
        <Card className="bg-green-50/80 border-green-200">
          <CardHeader className="pb-2">
            <div className="flex items-center gap-2">
              <IoCheckmarkCircleOutline className="h-4 w-4 text-green-600" />
              <CardTitle className="text-sm font-medium text-green-700">
                検索完了
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent className="pt-2">
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <IoSearchOutline className="h-4 w-4 text-green-600" />
                <span className="font-medium text-green-800">検索キーワード:</span>
                <Badge variant="secondary" className="bg-green-100 text-green-800">
                  {searchQuery.query}
                </Badge>
              </div>
              <div className="flex items-center gap-2 text-xs text-green-600">
                <IoTimeOutline className="h-3 w-3" />
                <span>
                  {new Date(searchQuery.timestamp).toLocaleString('ja-JP', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </span>
                {searchQuery.results_count && (
                  <>
                    <span className="mx-1">•</span>
                    <span>{searchQuery.results_count.toLocaleString()}件の結果</span>
                  </>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 検索結果表示 */}
      {searchResults && searchResults.length > 0 && (
        <Card className="bg-white/95 border-gray-200">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <IoGlobeOutline className="h-4 w-4 text-gray-600" />
                <CardTitle className="text-sm font-medium text-gray-700">
                  参照したWeb情報
                </CardTitle>
              </div>
              <Badge variant="outline" className="text-xs">
                {searchResults.length}件
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {searchResults.map((result, index) => (
                <div
                  key={index}
                  className="group p-3 rounded-lg border border-gray-100 hover:border-gray-200 hover:bg-gray-50/50 transition-all duration-200"
                >
                  <div className="space-y-2">
                    {/* タイトルとURL */}
                    <div className="space-y-1">
                      <h4 className="text-sm font-medium text-gray-900 group-hover:text-blue-700 transition-colors line-clamp-2">
                        {result.title}
                      </h4>
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <IoLinkOutline className="h-3 w-3 flex-shrink-0" />
                        <span className="truncate">
                          {result.displayLink || new URL(result.url).hostname}
                        </span>
                        {result.position && (
                          <>
                            <span>•</span>
                            <span>#{result.position}</span>
                          </>
                        )}
                      </div>
                    </div>
                    
                    {/* スニペット */}
                    {result.snippet && (
                      <p className="text-xs text-gray-600 line-clamp-2 leading-relaxed">
                        {result.snippet}
                      </p>
                    )}
                    
                    {/* 外部リンクボタン */}
                    <div className="flex justify-end">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 px-2 text-xs text-gray-500 hover:text-blue-600 hover:bg-blue-50"
                        onClick={() => window.open(result.url, '_blank', 'noopener,noreferrer')}
                      >
                        <IoLinkOutline className="h-3 w-3 mr-1" />
                        詳細を見る
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            {/* 注意事項 */}
            <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <div className="flex items-start gap-2">
                <IoInformationCircleOutline className="h-4 w-4 text-amber-600 flex-shrink-0 mt-0.5" />
                <div className="text-xs text-amber-700">
                  <p className="font-medium mb-1">情報の利用について</p>
                  <p className="leading-relaxed">
                    上記の情報は検索時点での内容です。最新の情報については、各サイトで直接ご確認ください。
                    重要な決定や医療に関する判断は、必ず専門家にご相談ください。
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
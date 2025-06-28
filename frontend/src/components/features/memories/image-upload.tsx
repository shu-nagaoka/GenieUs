'use client'

import React, { useState, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Upload, X, Image as ImageIcon, AlertCircle, Loader2 } from 'lucide-react'
import { uploadImage, getImageUrl } from '@/libs/api/file-upload'

interface ImageUploadProps {
  onImageUploaded: (fileUrl: string) => void
  onImageRemove: () => void
  currentImageUrl?: string
  disabled?: boolean
  className?: string
}

export function ImageUpload({
  onImageUploaded,
  onImageRemove,
  currentImageUrl,
  disabled = false,
  className = '',
}: ImageUploadProps) {
  const [preview, setPreview] = useState<string | null>(currentImageUrl || null)
  const [error, setError] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // ファイルサイズチェック (5MB制限)
    if (file.size > 5 * 1024 * 1024) {
      setError('ファイルサイズは5MB以下にしてください')
      return
    }

    // ファイル形式チェック
    if (!file.type.startsWith('image/')) {
      setError('画像ファイルを選択してください')
      return
    }

    setError(null)
    setIsUploading(true)

    try {
      // プレビューを作成
      const reader = new FileReader()
      reader.onload = e => {
        const result = e.target?.result as string
        setPreview(result)
      }
      reader.readAsDataURL(file)

      // バックエンドにアップロード
      const uploadResult = await uploadImage(file)

      if (uploadResult.success && uploadResult.file_url) {
        // 親コンポーネントにアップロード済みURLを通知
        onImageUploaded(uploadResult.file_url)
      } else {
        setError(uploadResult.message || 'アップロードに失敗しました')
        setPreview(null)
      }
    } catch (error) {
      console.error('Upload error:', error)
      setError('アップロード中にエラーが発生しました')
      setPreview(null)
    } finally {
      setIsUploading(false)
    }
  }

  const handleRemove = () => {
    setPreview(null)
    setError(null)
    onImageRemove()

    // ファイル入力をリセット
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className={`space-y-2 ${className}`}>
      <Label className="flex items-center gap-2 text-sm font-medium text-gray-700">
        <ImageIcon className="h-4 w-4" />
        画像アップロード
      </Label>

      {preview ? (
        // 画像プレビュー表示
        <div className="relative">
          <div className="h-48 w-full overflow-hidden rounded-lg border-2 border-cyan-200 bg-gray-100">
            <img src={preview} alt="プレビュー" className="h-full w-full object-cover" />
          </div>

          {/* 削除ボタン */}
          <button
            type="button"
            onClick={handleRemove}
            disabled={disabled}
            className="absolute right-2 top-2 rounded-full bg-red-500 p-1 text-white transition-colors hover:bg-red-600 disabled:opacity-50"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ) : (
        // アップロードエリア表示
        <div
          onClick={!isUploading ? handleUploadClick : undefined}
          className={`h-48 w-full rounded-lg border-2 border-dashed border-cyan-300 bg-cyan-50 transition-colors hover:bg-cyan-100 ${!isUploading ? 'cursor-pointer' : 'cursor-not-allowed'} flex flex-col items-center justify-center`}
        >
          {isUploading ? (
            <>
              <Loader2 className="mb-2 h-12 w-12 animate-spin text-cyan-400" />
              <p className="mb-1 text-sm font-medium text-cyan-700">アップロード中...</p>
            </>
          ) : (
            <>
              <Upload className="mb-2 h-12 w-12 text-cyan-400" />
              <p className="mb-1 text-sm font-medium text-cyan-700">
                クリックして画像をアップロード
              </p>
              <p className="text-xs text-cyan-600">JPEG, PNG, GIF (最大5MB)</p>
            </>
          )}
        </div>
      )}

      {/* エラーメッセージ */}
      {error && (
        <div className="flex items-center gap-2 text-sm text-red-600">
          <AlertCircle className="h-4 w-4" />
          <span>{error}</span>
        </div>
      )}

      {/* 隠しファイル入力 */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        disabled={disabled || isUploading}
        className="hidden"
      />

      {/* アップロードボタン（プレビューがない場合の代替） */}
      {!preview && !isUploading && (
        <Button
          type="button"
          variant="outline"
          onClick={handleUploadClick}
          disabled={disabled || isUploading}
          className="w-full border-cyan-300 text-cyan-700 hover:bg-cyan-50"
        >
          <Upload className="mr-2 h-4 w-4" />
          画像を選択
        </Button>
      )}
    </div>
  )
}

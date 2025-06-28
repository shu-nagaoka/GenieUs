'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Mic,
  MicOff,
  Square,
  Play,
  Pause,
  CheckCircle,
  AlertCircle,
  Loader2,
  Sparkles,
} from 'lucide-react'

interface VoiceRecordingResult {
  status: string
  message: string
  extracted_events: number
  events: any[]
  raw_text: string
}

interface FloatingVoiceButtonProps {
  className?: string
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left'
}

export function FloatingVoiceButton({
  className = '',
  position = 'bottom-right',
}: FloatingVoiceButtonProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [transcription, setTranscription] = useState('')
  const [result, setResult] = useState<VoiceRecordingResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const recognitionRef = useRef<any>(null)

  const getPositionClasses = () => {
    switch (position) {
      case 'bottom-right':
        return 'bottom-6 right-6'
      case 'bottom-left':
        return 'bottom-6 left-6'
      case 'top-right':
        return 'top-6 right-6'
      case 'top-left':
        return 'top-6 left-6'
      default:
        return 'bottom-6 right-6'
    }
  }

  // Web Speech API の初期化
  useEffect(() => {
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = true
      recognitionRef.current.interimResults = true
      recognitionRef.current.lang = 'ja-JP'

      recognitionRef.current.onresult = (event: any) => {
        let finalTranscript = ''
        let interimTranscript = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += transcript
          } else {
            interimTranscript += transcript
          }
        }

        setTranscription(finalTranscript + interimTranscript)
      }

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setError(`音声認識エラー: ${event.error}`)
      }
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

      mediaRecorderRef.current = new MediaRecorder(stream)
      audioChunksRef.current = []

      mediaRecorderRef.current.ondataavailable = event => {
        audioChunksRef.current.push(event.data)
      }

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        const url = URL.createObjectURL(audioBlob)
        setAudioUrl(url)
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorderRef.current.start()
      setIsRecording(true)
      setIsPaused(false)
      setRecordingTime(0)
      setTranscription('')
      setResult(null)
      setError(null)

      // 音声認識開始
      if (recognitionRef.current) {
        recognitionRef.current.start()
      }

      // タイマー開始
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)
    } catch (err) {
      setError('マイクへのアクセスが拒否されました')
      console.error('Error accessing microphone:', err)
    }
  }

  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      if (isPaused) {
        mediaRecorderRef.current.resume()
        if (recognitionRef.current) {
          recognitionRef.current.start()
        }
        timerRef.current = setInterval(() => {
          setRecordingTime(prev => prev + 1)
        }, 1000)
      } else {
        mediaRecorderRef.current.pause()
        if (recognitionRef.current) {
          recognitionRef.current.stop()
        }
        if (timerRef.current) {
          clearInterval(timerRef.current)
        }
      }
      setIsPaused(!isPaused)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
      setIsRecording(false)
      setIsPaused(false)
    }
  }

  const processVoiceRecord = async () => {
    if (!transcription.trim()) {
      setError('音声が認識されませんでした。もう一度お試しください。')
      return
    }

    setIsProcessing(true)
    setError(null)

    try {
      const response = await fetch('/api/v2/voice-record', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          voice_text: transcription,
          child_id: 'default_child',
          parent_id: 'default_parent',
        }),
      })

      if (!response.ok) {
        throw new Error(`処理に失敗しました: ${response.status}`)
      }

      const data: VoiceRecordingResult = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : '音声処理中にエラーが発生しました')
    } finally {
      setIsProcessing(false)
    }
  }

  const resetRecording = () => {
    setRecordingTime(0)
    setTranscription('')
    setResult(null)
    setError(null)
    setAudioUrl(null)
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <>
      {/* フローティングボタン */}
      <Button
        onClick={() => setIsOpen(true)}
        className={`fixed ${getPositionClasses()} ${className} group z-50 h-14 w-14 rounded-full border-0 bg-gradient-to-br from-emerald-400 to-teal-500 shadow-lg transition-all duration-300 hover:from-emerald-500 hover:to-teal-600 hover:shadow-xl`}
        size="icon"
      >
        <div className="flex items-center justify-center">
          <Mic className="h-6 w-6 text-white transition-transform group-hover:scale-110" />
          <div className="absolute -right-1 -top-1 h-3 w-3 animate-pulse rounded-full bg-red-400" />
        </div>
      </Button>

      {/* 録音ダイアログ */}
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-emerald-700">
              <Sparkles className="h-5 w-5" />
              音声で記録
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-6">
            {/* 録音コントロール */}
            <div className="space-y-4 text-center">
              {!isRecording && !transcription && (
                <div>
                  <p className="mb-4 text-sm text-gray-600">
                    「さっき10時にミルク150ml飲んで、すぐ寝ちゃった」のように自然に話してください
                  </p>
                  <Button
                    onClick={startRecording}
                    className="bg-emerald-500 hover:bg-emerald-600"
                    size="lg"
                  >
                    <Mic className="mr-2 h-5 w-5" />
                    録音開始
                  </Button>
                </div>
              )}

              {isRecording && (
                <div className="space-y-4">
                  <div className="flex items-center justify-center gap-4">
                    <div
                      className={`h-16 w-16 rounded-full ${isPaused ? 'bg-yellow-100' : 'bg-red-100'} flex items-center justify-center`}
                    >
                      {isPaused ? (
                        <Pause className="h-8 w-8 text-yellow-600" />
                      ) : (
                        <div className="h-4 w-4 animate-pulse rounded-full bg-red-500" />
                      )}
                    </div>
                  </div>

                  <div className="font-mono text-2xl text-gray-700">
                    {formatTime(recordingTime)}
                  </div>

                  <div className="flex justify-center gap-2">
                    <Button onClick={pauseRecording} variant="outline" size="sm">
                      {isPaused ? <Play className="h-4 w-4" /> : <Pause className="h-4 w-4" />}
                    </Button>
                    <Button
                      onClick={stopRecording}
                      variant="outline"
                      size="sm"
                      className="border-red-300 text-red-600 hover:bg-red-50"
                    >
                      <Square className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}
            </div>

            {/* 音声認識結果 */}
            {transcription && (
              <div className="space-y-4">
                <div>
                  <h4 className="mb-2 text-sm font-medium text-gray-700">認識されたテキスト</h4>
                  <div className="rounded-lg border bg-gray-50 p-3">
                    <p className="text-sm text-gray-700">{transcription || '音声を認識中...'}</p>
                  </div>
                </div>

                {!isRecording && !isProcessing && !result && (
                  <div className="flex gap-2">
                    <Button
                      onClick={processVoiceRecord}
                      className="flex-1 bg-emerald-500 hover:bg-emerald-600"
                    >
                      記録として保存
                    </Button>
                    <Button onClick={resetRecording} variant="outline" className="border-gray-300">
                      やり直し
                    </Button>
                  </div>
                )}
              </div>
            )}

            {/* 処理中 */}
            {isProcessing && (
              <div className="space-y-3 text-center">
                <Loader2 className="mx-auto h-8 w-8 animate-spin text-emerald-600" />
                <p className="text-sm text-gray-600">AIが音声を分析しています...</p>
                <Progress value={50} className="h-2" />
              </div>
            )}

            {/* 処理結果 */}
            {result && (
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-green-700">
                  <CheckCircle className="h-5 w-5" />
                  <span className="font-medium">記録完了</span>
                </div>

                <div className="rounded-lg border border-green-200 bg-green-50 p-4">
                  <p className="mb-2 text-sm text-green-800">{result.message}</p>
                  {result.extracted_events > 0 && (
                    <Badge variant="secondary" className="bg-green-100 text-green-700">
                      {result.extracted_events}件のイベントを記録
                    </Badge>
                  )}
                </div>

                <Button
                  onClick={() => {
                    resetRecording()
                    setIsOpen(false)
                  }}
                  className="w-full bg-emerald-500 hover:bg-emerald-600"
                >
                  完了
                </Button>
              </div>
            )}

            {/* エラー表示 */}
            {error && (
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-red-700">
                  <AlertCircle className="h-5 w-5" />
                  <span className="font-medium">エラー</span>
                </div>

                <div className="rounded-lg border border-red-200 bg-red-50 p-4">
                  <p className="text-sm text-red-800">{error}</p>
                </div>

                <Button
                  onClick={resetRecording}
                  variant="outline"
                  className="w-full border-red-300 text-red-600 hover:bg-red-50"
                >
                  もう一度試す
                </Button>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

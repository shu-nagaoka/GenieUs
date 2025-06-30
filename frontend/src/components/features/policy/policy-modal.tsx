'use client'

import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { HiOutlineDocumentText } from 'react-icons/hi2'

interface PolicyModalProps {
  trigger?: React.ReactNode
}

export function PolicyModal({ trigger }: PolicyModalProps) {
  const [open, setOpen] = useState(false)

  const defaultTrigger = (
    <Button
      variant="ghost"
      size="sm"
      className="h-8 w-full justify-start gap-2 text-xs text-gray-600 hover:text-gray-900"
    >
      <HiOutlineDocumentText className="h-3 w-3" />
      ポリシー・規約
    </Button>
  )

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || defaultTrigger}
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <HiOutlineDocumentText className="h-5 w-5" />
            GenieUs ポリシー・規約
            <Badge variant="secondary" className="text-xs">
              ベータ版
            </Badge>
          </DialogTitle>
        </DialogHeader>
        
        <Tabs defaultValue="beta-notice" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="beta-notice">ベータ版について</TabsTrigger>
            <TabsTrigger value="terms">利用規約</TabsTrigger>
            <TabsTrigger value="license">ライセンス</TabsTrigger>
          </TabsList>
          
          <TabsContent value="beta-notice" className="mt-4">
            <ScrollArea className="h-[400px] w-full rounded-md border p-4">
              <div className="space-y-4">
                <div className="rounded-lg bg-yellow-50 border border-yellow-200 p-4">
                  <h3 className="font-semibold text-yellow-800 mb-2">
                    ⚠️ ベータ版に関する重要なお知らせ
                  </h3>
                  <p className="text-yellow-700">
                    GenieUsは現在開発中のベータ版アプリケーションです。以下の点にご注意ください。
                  </p>
                </div>

                <div className="space-y-3">
                  <h4 className="font-medium text-gray-900">データの自動削除について</h4>
                  <p className="text-gray-700">
                    本アプリケーションに登録されたデータ（家族情報、記録、チャット履歴等）は、
                    <strong className="text-red-600">一定期間経過後に自動的に削除</strong>されます。
                    重要なデータについては、定期的にバックアップを取得することを強く推奨いたします。
                  </p>

                  <h4 className="font-medium text-gray-900">サービスの安定性について</h4>
                  <p className="text-gray-700">
                    ベータ版のため、予期しないエラーやサービス停止が発生する可能性があります。
                    本番環境での利用や重要な業務での使用は避けてください。
                  </p>

                  <h4 className="font-medium text-gray-900">フィードバックのお願い</h4>
                  <p className="text-gray-700">
                    より良いサービス提供のため、バグ報告や機能改善の提案をお待ちしております。
                    ご意見・ご要望がございましたら、開発チームまでお寄せください。
                  </p>

                  <h4 className="font-medium text-gray-900">商用利用の禁止</h4>
                  <p className="text-gray-700">
                    本ベータ版は<strong className="text-red-600">検証・テスト目的のみ</strong>での利用を想定しており、
                    商用利用は禁止されています。
                  </p>
                </div>
              </div>
            </ScrollArea>
          </TabsContent>
          
          <TabsContent value="terms" className="mt-4">
            <ScrollArea className="h-[400px] w-full rounded-md border p-4">
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">利用規約</h3>
                
                <div className="space-y-3">
                  <h4 className="font-medium text-gray-900">第1条（適用範囲）</h4>
                  <p className="text-gray-700">
                    本規約は、GenieUs（以下「本サービス」）の利用に関する条件を定めるものです。
                    本サービスを利用する全てのユーザーは、本規約に同意したものとみなします。
                  </p>

                  <h4 className="font-medium text-gray-900">第2条（利用目的）</h4>
                  <p className="text-gray-700">
                    本サービスは、AI技術を活用した子育て支援を目的としたアプリケーションです。
                    検証・テスト目的での利用に限定され、商用利用は禁止されています。
                  </p>

                  <h4 className="font-medium text-gray-900">第3条（データの取り扱い）</h4>
                  <p className="text-gray-700">
                    ユーザーが本サービスに入力したデータは、サービス改善のため匿名化された形で
                    分析に使用される場合があります。個人を特定できる情報の第三者提供は行いません。
                  </p>

                  <h4 className="font-medium text-gray-900">第4条（免責事項）</h4>
                  <p className="text-gray-700">
                    本サービスの提供者は、サービスの中断、エラー、データの消失等による
                    損害について一切の責任を負いません。ユーザーの自己責任での利用をお願いします。
                  </p>

                  <h4 className="font-medium text-gray-900">第5条（禁止事項）</h4>
                  <ul className="text-gray-700 list-disc list-inside space-y-1">
                    <li>法令に違反する行為</li>
                    <li>他のユーザーに迷惑をかける行為</li>
                    <li>サービスの正常な運営を妨げる行為</li>
                    <li>商用目的での利用</li>
                    <li>知的財産権を侵害する行為</li>
                  </ul>
                </div>
              </div>
            </ScrollArea>
          </TabsContent>
          
          <TabsContent value="license" className="mt-4">
            <ScrollArea className="h-[400px] w-full rounded-md border p-4">
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">ライセンス情報</h3>
                
                <div className="space-y-3">
                  <h4 className="font-medium text-gray-900">著作権</h4>
                  <p className="text-gray-700">
                    GenieUsアプリケーションの著作権は開発者に帰属します。
                    <br />
                    <strong>All Rights Reserved.</strong>
                  </p>

                  <h4 className="font-medium text-gray-900">使用許諾</h4>
                  <p className="text-gray-700">
                    本ソフトウェアは、個人的な検証・テスト目的での使用のみ許可されています。
                    以下の行為は禁止されています：
                  </p>
                  <ul className="text-gray-700 list-disc list-inside space-y-1">
                    <li>商用利用</li>
                    <li>再配布</li>
                    <li>改変・修正</li>
                    <li>リバースエンジニアリング</li>
                  </ul>

                  <h4 className="font-medium text-gray-900">第三者ライブラリ</h4>
                  <p className="text-gray-700">
                    本アプリケーションは以下のオープンソースライブラリを使用しています：
                  </p>
                  <ul className="text-gray-700 list-disc list-inside space-y-1">
                    <li>React (MIT License)</li>
                    <li>Next.js (MIT License)</li>
                    <li>Tailwind CSS (MIT License)</li>
                    <li>shadcn/ui (MIT License)</li>
                    <li>その他のライブラリについてはpackage.jsonを参照</li>
                  </ul>

                  <h4 className="font-medium text-gray-900">免責事項</h4>
                  <p className="text-gray-700">
                    本ソフトウェアは「現状のまま」提供され、明示的または暗示的な保証は一切ありません。
                    使用によって生じたいかなる損害についても、開発者は責任を負いません。
                  </p>
                </div>
              </div>
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}
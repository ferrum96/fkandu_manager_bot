import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  const board = await prisma.board.findUnique({
    where: { id },
    include: {
      columns: {
        orderBy: { position: 'asc' },
        include: {
          tasks: {
            orderBy: { position: 'asc' },
            include: {
              epic: true,
              labels: { include: { label: true } },
            },
          },
        },
      },
      epics: true,
      labels: true,
    },
  })

  if (!board) {
    return NextResponse.json({ error: 'Board not found' }, { status: 404 })
  }

  return NextResponse.json(board)
}

export async function PUT(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  const body = await request.json()

  const board = await prisma.board.update({
    where: { id },
    data: { name: body.name },
  })

  return NextResponse.json(board)
}

export async function DELETE(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  await prisma.board.delete({ where: { id } })
  return NextResponse.json({ success: true })
}

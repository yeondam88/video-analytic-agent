import React from 'react'
import { Chat } from '@/components/Chat/Chat'
import { motion } from 'framer-motion'

const containerVariants = {
  initial: { opacity: 0 },
  animate: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

const itemVariants = {
  initial: { opacity: 0, y: 20 },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: "easeOut"
    }
  }
}

export function ChatPage() {
  return (
    <motion.div 
      className="space-y-6"
      variants={containerVariants}
      initial="initial"
      animate="animate"
    >
      <motion.div 
        className="flex items-center justify-between"
        variants={itemVariants}
      >
        <h1 className="text-3xl font-bold">Video Assistant</h1>
      </motion.div>
      <div className="grid gap-6 md:grid-cols-[2fr_1fr]">
        <motion.div variants={itemVariants}>
          <Chat />
        </motion.div>
        <motion.div className="space-y-6" variants={itemVariants}>
          <motion.div 
            className="rounded-lg border bg-card p-4"
            variants={itemVariants}
          >
            <h3 className="mb-2 font-semibold">Tips</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <motion.li variants={itemVariants}>• Ask questions about any video in your library</motion.li>
              <motion.li variants={itemVariants}>• Get summaries and key points</motion.li>
              <motion.li variants={itemVariants}>• Search for specific moments</motion.li>
              <motion.li variants={itemVariants}>• Analyze speaker insights</motion.li>
            </ul>
          </motion.div>
          <motion.div 
            className="rounded-lg border bg-card p-4"
            variants={itemVariants}
          >
            <h3 className="mb-2 font-semibold">Example Questions</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <motion.li variants={itemVariants}>• "What are the main points from the latest video?"</motion.li>
              <motion.li variants={itemVariants}>• "Find moments where we discuss project timeline"</motion.li>
              <motion.li variants={itemVariants}>• "Who spoke the most in this meeting?"</motion.li>
              <motion.li variants={itemVariants}>• "Generate a summary of all action items"</motion.li>
            </ul>
          </motion.div>
        </motion.div>
      </div>
    </motion.div>
  )
} 
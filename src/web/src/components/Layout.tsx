import React, { useState } from 'react'
import { Sidebar, SidebarBody, SidebarLink } from './Sidebar'
import { Home, MessageSquare } from 'lucide-react'
import { AuroraBackground } from './AuroraBackground'

const sidebarLinks = [
  {
    label: "Home",
    href: "/",
    icon: <Home className="w-5 h-5" />,
  },
  // {
  //   label: "Videos",
  //   href: "/videos",
  //   icon: <Video className="w-5 h-5" />,
  // },
  {
    label: "Chat",
    href: "/chat",
    icon: <MessageSquare className="w-5 h-5" />,
  },
  // {
  //   label: "Search",
  //   href: "/search",
  //   icon: <Search className="w-5 h-5" />,
  // }
]

interface LayoutProps {
  children: React.ReactNode
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative w-full min-h-screen">
      <AuroraBackground>
        <div className="flex w-full min-h-screen relative">
          <Sidebar open={isOpen} setOpen={setIsOpen}>
            <SidebarBody className="bg-white/90 dark:bg-neutral-900/90 backdrop-blur-md border-r border-neutral-200 dark:border-neutral-800">
              <div className="flex flex-col justify-between h-full">
                <div className="space-y-4">
                  <div className="mb-6">
                    <h2 className="text-lg font-bold text-neutral-800 dark:text-neutral-200">
                      Clay AI
                    </h2>
                  </div>
                  <nav className="space-y-1">
                    {sidebarLinks.map((link) => (
                      <SidebarLink 
                        key={link.href} 
                        link={link}
                        className="hover:bg-neutral-100 dark:hover:bg-neutral-800/50 rounded-lg transition-colors"
                      />
                    ))}
                  </nav>
                </div>
              </div>
            </SidebarBody>
          </Sidebar>
          <main className="flex-1 p-6 overflow-auto w-full relative z-0">
            {children}
          </main>
        </div>
      </AuroraBackground>
    </div>
  )
} 
import { useState, useEffect, useRef, useCallback } from 'react'

export function useScrollSpy(sectionIds: string[]) {
  const [activeId, setActiveId] = useState<string | null>(null)
  const isScrolling = useRef(false)

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (isScrolling.current) return
        const visible = entries
          .filter(e => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
        if (visible.length > 0) {
          setActiveId(visible[0].target.id.replace('section-', ''))
        }
      },
      { rootMargin: '-10% 0px -60% 0px', threshold: 0 }
    )
    sectionIds.forEach(id => {
      const el = document.getElementById(`section-${id}`)
      if (el) observer.observe(el)
    })
    return () => observer.disconnect()
  }, [sectionIds])

  const scrollToSection = useCallback((id: string) => {
    isScrolling.current = true
    document.getElementById(`section-${id}`)?.scrollIntoView({ behavior: 'smooth' })
    setTimeout(() => { isScrolling.current = false }, 600)
  }, [])

  return { activeId, scrollToSection }
}

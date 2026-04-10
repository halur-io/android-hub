export function FlowTabsLoad() {
  return (
    <div className="min-h-screen bg-[#f8f9fa]" dir="rtl" style={{ fontFamily: "'Segoe UI', Tahoma, sans-serif" }}>
      <style>{`
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        .skeleton {
          background: linear-gradient(90deg, #e5e7eb 25%, #f3f4f6 50%, #e5e7eb 75%);
          background-size: 200% 100%;
          animation: shimmer 1.5s infinite ease-in-out;
          border-radius: 8px;
        }
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(-8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .slide-in { animation: slideIn 0.3s ease-out both; }
      `}</style>

      {/* Header */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-[#1e1b4b] text-white shadow-lg" style={{ height: 56 }}>
        <div className="flex items-center justify-between px-4 h-full">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-white/20" />
            <span className="font-bold text-sm">SUMO</span>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <span>סניף ראמה</span>
            <span className="bg-white/20 px-2 py-0.5 rounded text-[10px]">HE</span>
          </div>
        </div>
      </div>

      <div style={{ height: 56 }} />

      {/* Order type bar */}
      <div className="bg-white border-b px-3 py-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="bg-[#e0e7ff] text-[#4338ca] px-3 py-1.5 rounded-full text-xs font-bold">
            🛵 משלוח
          </div>
          <div className="bg-gray-100 text-gray-500 px-3 py-1.5 rounded-full text-xs font-bold">
            🛍️ איסוף
          </div>
        </div>
      </div>

      <div className="px-3 pt-4">
        {/* REAL category tabs - loaded! With green checkmark pulse */}
        <div className="flex gap-2 mb-4 overflow-x-auto pb-2 slide-in relative">
          {[
            { name: '🔥 מבצעים', active: true },
            { name: 'המבורגרים', active: false },
            { name: 'פיצות', active: false },
            { name: 'סלטים', active: false },
            { name: 'שתייה', active: false },
          ].map((cat, i) => (
            <div
              key={i}
              className="flex-shrink-0 px-4 font-bold text-xs"
              style={{
                height: 34,
                lineHeight: '34px',
                borderRadius: 17,
                border: `2px solid ${cat.active ? '#4338ca' : '#e0e7ff'}`,
                background: cat.active ? '#4338ca' : 'white',
                color: cat.active ? 'white' : '#4338ca',
                whiteSpace: 'nowrap',
              }}
            >
              {cat.name}
            </div>
          ))}
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full flex items-center justify-center">
            <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round"><polyline points="20 6 9 17 4 12" /></svg>
          </div>
        </div>

        {/* Section title - REAL */}
        <div className="mb-2 slide-in" style={{ fontSize: 16, fontWeight: 800, color: '#1e1b4b', textAlign: 'right', paddingRight: 2 }}>
          <span style={{ color: '#ef4444', marginLeft: 6, fontSize: 14 }}>🔥</span> מבצעים
        </div>

        {/* Cards still skeleton - not loaded yet */}
        <div className="flex gap-3 overflow-x-auto pb-3" style={{ direction: 'rtl' }}>
          {[1, 2, 3].map(i => (
            <div key={i} className="flex-shrink-0 bg-white overflow-hidden" style={{ width: 140, borderRadius: 14, boxShadow: '0 1px 5px rgba(0,0,0,.09)' }}>
              <div className="skeleton" style={{ width: '100%', paddingTop: '88%', borderRadius: 0 }} />
              <div className="p-2 space-y-2">
                <div className="skeleton" style={{ width: '80%', height: 12 }} />
                <div className="skeleton" style={{ width: '50%', height: 10 }} />
                <div className="skeleton" style={{ width: '40%', height: 14 }} />
              </div>
            </div>
          ))}
        </div>

        {/* Section 2 title - REAL */}
        <div className="mb-2 mt-4 slide-in" style={{ fontSize: 16, fontWeight: 800, color: '#1e1b4b', textAlign: 'right', paddingRight: 2, animationDelay: '0.1s' }}>
          המבורגרים
        </div>

        {/* Cards still skeleton */}
        <div className="flex gap-3 overflow-x-auto pb-3" style={{ direction: 'rtl' }}>
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="flex-shrink-0 bg-white overflow-hidden" style={{ width: 140, borderRadius: 14, boxShadow: '0 1px 5px rgba(0,0,0,.09)' }}>
              <div className="skeleton" style={{ width: '100%', paddingTop: '88%', borderRadius: 0 }} />
              <div className="p-2 space-y-2">
                <div className="skeleton" style={{ width: '75%', height: 12 }} />
                <div className="skeleton" style={{ width: '35%', height: 14 }} />
              </div>
            </div>
          ))}
        </div>

        {/* Section 3 title */}
        <div className="mb-2 mt-4 slide-in" style={{ fontSize: 16, fontWeight: 800, color: '#1e1b4b', textAlign: 'right', paddingRight: 2, animationDelay: '0.15s' }}>
          פיצות
        </div>
        <div className="flex gap-3 overflow-x-auto pb-3" style={{ direction: 'rtl' }}>
          {[1, 2, 3].map(i => (
            <div key={i} className="flex-shrink-0 bg-white overflow-hidden" style={{ width: 140, borderRadius: 14, boxShadow: '0 1px 5px rgba(0,0,0,.09)' }}>
              <div className="skeleton" style={{ width: '100%', paddingTop: '88%', borderRadius: 0 }} />
              <div className="p-2 space-y-2">
                <div className="skeleton" style={{ width: '85%', height: 12 }} />
                <div className="skeleton" style={{ width: '45%', height: 14 }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Stage indicator */}
      <div className="fixed bottom-4 left-4 right-4 bg-[#1e1b4b] text-white rounded-xl p-3 shadow-xl flex items-center gap-3 z-50">
        <div className="flex items-center gap-2 flex-shrink-0">
          <div className="w-6 h-6 rounded-full bg-emerald-500 text-white text-[10px] font-bold flex items-center justify-center">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round"><polyline points="20 6 9 17 4 12" /></svg>
          </div>
          <div className="w-4 h-[2px] bg-[#4338ca]" />
          <div className="w-6 h-6 rounded-full bg-[#4338ca] text-white text-[10px] font-bold flex items-center justify-center">2</div>
          <div className="w-4 h-[2px] bg-white/30" />
          <div className="w-6 h-6 rounded-full bg-white/20 text-white/40 text-[10px] font-bold flex items-center justify-center">3</div>
        </div>
        <div className="mr-2">
          <div className="text-xs font-bold">Categories load → Replace tab skeletons</div>
          <div className="text-[10px] opacity-70">Real tabs slide in, cards still loading</div>
        </div>
      </div>
    </div>
  );
}

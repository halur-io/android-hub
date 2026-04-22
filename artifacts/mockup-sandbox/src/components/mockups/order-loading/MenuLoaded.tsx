export function MenuLoaded() {
  return (
    <div className="min-h-screen bg-[#f8f9fa]" dir="rtl" style={{ fontFamily: "'Segoe UI', Tahoma, sans-serif" }}>
      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(12px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .fade-in { animation: fadeInUp 0.4s ease-out both; }
        .fade-in-d1 { animation-delay: 0.05s; }
        .fade-in-d2 { animation-delay: 0.1s; }
        .fade-in-d3 { animation-delay: 0.15s; }
        .fade-in-d4 { animation-delay: 0.2s; }
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
        {/* Category tabs - styled */}
        <div className="flex gap-2 mb-4 overflow-x-auto pb-2 fade-in">
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
        </div>

        {/* Section: מבצעים */}
        <div className="mb-2 fade-in fade-in-d1" style={{ fontSize: 16, fontWeight: 800, color: '#1e1b4b', textAlign: 'right', paddingRight: 2 }}>
          <span style={{ color: '#ef4444', marginLeft: 6, fontSize: 14 }}>🔥</span> מבצעים
        </div>
        <div className="flex gap-3 overflow-x-auto pb-3 fade-in fade-in-d2" style={{ direction: 'rtl' }}>
          {[
            { name: 'ארוחת המבורגר', desc: 'המבורגר + צ׳יפס + שתייה', price: 59, badge: true },
            { name: 'פיצה משפחתית', desc: 'פיצה XL + 2 תוספות', price: 45, badge: true },
            { name: 'קומבו ילדים', desc: 'נאגטס + צ׳יפס + שתייה', price: 35, badge: true },
          ].map((item, i) => (
            <div
              key={i}
              className="flex-shrink-0 bg-white overflow-hidden relative"
              style={{
                width: 140,
                borderRadius: 14,
                boxShadow: '0 1px 5px rgba(0,0,0,.09)',
              }}
            >
              <div style={{ width: '100%', paddingTop: '88%', position: 'relative', overflow: 'hidden' }}>
                <div className="absolute inset-0" style={{
                  background: `linear-gradient(135deg, ${['#fef3c7', '#fee2e2', '#dbeafe'][i]} 0%, ${['#fde68a', '#fca5a5', '#93c5fd'][i]} 100%)`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 36,
                }}>
                  {['🍔', '🍕', '🍗'][i]}
                </div>
              </div>
              {item.badge && (
                <div className="absolute top-2 left-2 bg-[#ef4444] text-white text-[9px] font-bold px-1.5 py-0.5 rounded-md flex items-center gap-0.5">
                  🔥 DEAL
                </div>
              )}
              <div style={{ padding: '8px 9px 10px', textAlign: 'right' }}>
                <div style={{ fontSize: 12.5, fontWeight: 700, color: '#1e1b4b', lineHeight: 1.3 }}>{item.name}</div>
                <div style={{ fontSize: 11, color: '#6b7280', lineHeight: 1.3, marginTop: 2 }}>{item.desc}</div>
                <div style={{ fontSize: 14.5, fontWeight: 800, color: '#16a34a', marginTop: 4 }}>₪{item.price}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Section: המבורגרים */}
        <div className="mb-2 mt-4 fade-in fade-in-d3" style={{ fontSize: 16, fontWeight: 800, color: '#1e1b4b', textAlign: 'right', paddingRight: 2 }}>
          המבורגרים
        </div>
        <div className="flex gap-3 overflow-x-auto pb-3 fade-in fade-in-d4" style={{ direction: 'rtl' }}>
          {[
            { name: 'קלאסי', price: 42 },
            { name: 'כפול', price: 52 },
            { name: 'מוקפץ', price: 48 },
            { name: 'BBQ', price: 55 },
          ].map((item, i) => (
            <div
              key={i}
              className="flex-shrink-0 bg-white overflow-hidden"
              style={{
                width: 140,
                borderRadius: 14,
                boxShadow: '0 1px 5px rgba(0,0,0,.09)',
              }}
            >
              <div style={{ width: '100%', paddingTop: '88%', position: 'relative', overflow: 'hidden' }}>
                <div className="absolute inset-0" style={{
                  background: `linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 36,
                }}>
                  🍔
                </div>
              </div>
              <div style={{ padding: '8px 9px 10px', textAlign: 'right' }}>
                <div style={{ fontSize: 12.5, fontWeight: 700, color: '#1e1b4b', lineHeight: 1.3 }}>{item.name}</div>
                <div style={{ fontSize: 14.5, fontWeight: 800, color: '#4338ca', marginTop: 4 }}>₪{item.price}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Success indicator */}
      <div className="fixed bottom-4 left-4 right-4 bg-emerald-600 text-white rounded-xl p-3 shadow-xl flex items-center gap-3 z-50">
        <div className="w-10 h-10 flex items-center justify-center flex-shrink-0 bg-white/20 rounded-full">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </div>
        <div>
          <div className="text-xs font-bold">Menu loaded — smooth fade-in</div>
          <div className="text-[10px] opacity-70">No FOUC, styled skeleton → content transition</div>
        </div>
      </div>
    </div>
  );
}

export function CurrentProblem() {
  return (
    <div className="min-h-screen bg-[#f8f9fa]" dir="rtl" style={{ fontFamily: "'Segoe UI', Tahoma, sans-serif" }}>
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

      {/* FOUC Simulation - black borders, unstyled content flash */}
      <div className="px-3 pt-4">
        {/* Category tabs - showing FOUC state with black borders */}
        <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
          {['מבצעים', 'המבורגרים', 'פיצות', 'סלטים', 'שתייה'].map((cat, i) => (
            <div
              key={i}
              className="flex-shrink-0 px-3 py-1.5 text-xs font-bold"
              style={{
                border: '2px solid black',
                borderRadius: 0,
                color: 'black',
                background: 'white',
                fontFamily: 'Times New Roman, serif',
              }}
            >
              {cat}
            </div>
          ))}
        </div>

        {/* Section title - unstyled */}
        <div className="mb-2" style={{ fontFamily: 'Times New Roman, serif', fontSize: 16, fontWeight: 'normal' }}>
          מבצעים
        </div>

        {/* FOUC cards - black background image areas, no rounded corners, serif font */}
        <div className="flex gap-3 overflow-x-auto pb-3" style={{ direction: 'rtl' }}>
          {[1, 2, 3].map(i => (
            <div
              key={i}
              className="flex-shrink-0"
              style={{
                width: 140,
                border: '1px solid black',
                borderRadius: 0,
                overflow: 'hidden',
                background: 'white',
              }}
            >
              <div style={{ width: '100%', paddingTop: '88%', background: '#000', position: 'relative' }}>
                <div className="absolute inset-0 flex items-center justify-center">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#555" strokeWidth="1">
                    <rect x="3" y="3" width="18" height="18" rx="2" />
                    <line x1="3" y1="3" x2="21" y2="21" />
                  </svg>
                </div>
              </div>
              <div className="p-2">
                <div style={{ fontFamily: 'Times New Roman, serif', fontSize: 14, color: 'black' }}>
                  {i === 1 ? 'ארוחת המבורגר' : i === 2 ? 'פיצה משפחתית' : 'קומבו ילדים'}
                </div>
                <div style={{ fontFamily: 'Times New Roman, serif', fontSize: 12, color: 'blue', textDecoration: 'underline' }}>
                  ₪{i === 1 ? 59 : i === 2 ? 45 : 35}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Another section - FOUC */}
        <div className="mb-2 mt-4" style={{ fontFamily: 'Times New Roman, serif', fontSize: 16, fontWeight: 'normal' }}>
          המבורגרים
        </div>
        <div className="flex gap-3 overflow-x-auto pb-3" style={{ direction: 'rtl' }}>
          {[1, 2, 3, 4].map(i => (
            <div
              key={i}
              className="flex-shrink-0"
              style={{
                width: 140,
                border: '1px solid black',
                borderRadius: 0,
                overflow: 'hidden',
                background: 'white',
              }}
            >
              <div style={{ width: '100%', paddingTop: '88%', background: '#000', position: 'relative' }} />
              <div className="p-2">
                <div style={{ fontFamily: 'Times New Roman, serif', fontSize: 14, color: 'black' }}>
                  {['קלאסי', 'כפול', 'מוקפץ', 'BBQ'][i - 1]}
                </div>
                <div style={{ fontFamily: 'Times New Roman, serif', fontSize: 12, color: 'blue', textDecoration: 'underline' }}>
                  ₪{[42, 52, 48, 55][i - 1]}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Warning overlay */}
      <div className="fixed bottom-4 left-4 right-4 bg-red-500 text-white rounded-xl p-3 shadow-xl flex items-center gap-3 z-50">
        <div className="bg-white/20 rounded-full w-10 h-10 flex items-center justify-center flex-shrink-0">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
        </div>
        <div>
          <div className="text-xs font-bold">FOUC — Flash of Unstyled Content</div>
          <div className="text-[10px] opacity-80">Black borders, serif font, broken images flash before CSS loads</div>
        </div>
      </div>
    </div>
  );
}

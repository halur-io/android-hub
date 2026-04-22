export function FlowInitial() {
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
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        .appear { animation: fadeIn 0.3s ease-out both; }
        .appear-d1 { animation-delay: 0.1s; }
        .appear-d2 { animation-delay: 0.2s; }
        .appear-d3 { animation-delay: 0.3s; }
      `}</style>

      {/* Header - loads instantly (server-rendered) */}
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

      {/* Order type bar - loads instantly */}
      <div className="bg-white border-b px-3 py-2 flex items-center justify-between appear">
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
        {/* Skeleton tabs appearing */}
        <div className="flex gap-2 mb-4 overflow-x-auto pb-2 appear appear-d1">
          {[72, 88, 60, 64, 56].map((w, i) => (
            <div key={i} className="skeleton flex-shrink-0" style={{ width: w, height: 34, borderRadius: 17 }} />
          ))}
        </div>

        {/* First section skeleton appearing */}
        <div className="appear appear-d2">
          <div className="skeleton mb-3" style={{ width: 80, height: 18 }} />
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
        </div>

        {/* Second section - still loading, partially visible */}
        <div className="appear appear-d3" style={{ opacity: 0.5 }}>
          <div className="skeleton mb-3 mt-4" style={{ width: 100, height: 18 }} />
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
        </div>
      </div>

      {/* Stage indicator */}
      <div className="fixed bottom-4 left-4 right-4 bg-[#1e1b4b] text-white rounded-xl p-3 shadow-xl flex items-center gap-3 z-50">
        <div className="flex items-center gap-2 flex-shrink-0">
          <div className="w-6 h-6 rounded-full bg-[#4338ca] text-white text-[10px] font-bold flex items-center justify-center">1</div>
          <div className="w-4 h-[2px] bg-white/30" />
          <div className="w-6 h-6 rounded-full bg-white/20 text-white/40 text-[10px] font-bold flex items-center justify-center">2</div>
          <div className="w-4 h-[2px] bg-white/30" />
          <div className="w-6 h-6 rounded-full bg-white/20 text-white/40 text-[10px] font-bold flex items-center justify-center">3</div>
        </div>
        <div className="mr-2">
          <div className="text-xs font-bold">Page opens → Skeleton appears</div>
          <div className="text-[10px] opacity-70">CSS loaded inline, skeleton renders instantly</div>
        </div>
      </div>
    </div>
  );
}

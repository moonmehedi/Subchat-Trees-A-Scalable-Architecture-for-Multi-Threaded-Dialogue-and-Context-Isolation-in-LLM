import React from 'react';
import { ArrowDown, ArrowUp, Merge } from 'lucide-react';

export default function HierarchicalContextFlow() {
  return (
    <div className="w-full h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-8 overflow-auto">
      <div className="max-w-6xl mx-auto">
        {/* Title */}
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Hierarchical Subchat Context Flow
          </h1>
          <p className="text-gray-600">Context Propagation and Aggregation Model</p>
        </div>

        {/* Main Visualization */}
        <div className="flex flex-col items-center space-y-8">
          
          {/* ROOT NODE */}
          <div className="relative">
            <div className="bg-gradient-to-r from-purple-600 to-purple-700 text-white px-12 py-6 rounded-2xl shadow-2xl border-4 border-purple-800">
              <div className="text-2xl font-bold text-center">ROOT</div>
              <div className="text-xs text-purple-200 text-center mt-1">Master Context Aggregator</div>
            </div>
          </div>

          {/* Downward Context Flow from Root */}
          <div className="flex justify-center items-center gap-4">
            <div className="flex flex-col items-center">
              <ArrowDown className="text-purple-600 animate-pulse" size={32} strokeWidth={3} />
              <div className="bg-purple-100 px-3 py-1 rounded text-xs font-semibold text-purple-700 mt-1">
                Root Context
              </div>
            </div>
          </div>

          {/* PARENT LEVEL */}
          <div className="flex gap-12 items-start">
            {/* Parent A */}
            <div className="flex flex-col items-center space-y-4">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-8 py-4 rounded-xl shadow-xl border-2 border-blue-700">
                <div className="text-xl font-bold text-center">Parent A</div>
              </div>
              
              {/* Context flow to children */}
              <div className="flex flex-col items-center">
                <ArrowDown className="text-blue-600" size={24} strokeWidth={2.5} />
                <div className="bg-blue-100 px-2 py-1 rounded text-xs font-semibold text-blue-700">
                  Parent A Context
                </div>
              </div>

              {/* Children A */}
              <div className="flex gap-4">
                <div className="flex flex-col items-center space-y-2">
                  <div className="bg-gradient-to-r from-cyan-400 to-cyan-500 text-white px-6 py-3 rounded-lg shadow-lg border border-cyan-600">
                    <div className="font-semibold text-center">Child A1</div>
                  </div>
                  <ArrowUp className="text-cyan-600" size={20} strokeWidth={2.5} />
                  <div className="bg-cyan-100 px-2 py-1 rounded text-xs font-semibold text-cyan-700">
                    A1 Context
                  </div>
                </div>
                
                <div className="flex flex-col items-center space-y-2">
                  <div className="bg-gradient-to-r from-cyan-400 to-cyan-500 text-white px-6 py-3 rounded-lg shadow-lg border border-cyan-600">
                    <div className="font-semibold text-center">Child A2</div>
                  </div>
                  <ArrowUp className="text-cyan-600" size={20} strokeWidth={2.5} />
                  <div className="bg-cyan-100 px-2 py-1 rounded text-xs font-semibold text-cyan-700">
                    A2 Context
                  </div>
                </div>
              </div>

              {/* Merge indicator for Parent A */}
              <div className="flex items-center gap-2 bg-blue-200 px-4 py-2 rounded-lg border-2 border-blue-400">
                <Merge className="text-blue-700" size={20} />
                <span className="text-sm font-bold text-blue-800">Merge: A1 + A2</span>
              </div>

              {/* Return to root */}
              <ArrowUp className="text-blue-600 animate-pulse" size={28} strokeWidth={3} />
            </div>

            {/* Parent B */}
            <div className="flex flex-col items-center space-y-4">
              <div className="bg-gradient-to-r from-green-500 to-green-600 text-white px-8 py-4 rounded-xl shadow-xl border-2 border-green-700">
                <div className="text-xl font-bold text-center">Parent B</div>
              </div>
              
              <div className="flex flex-col items-center">
                <ArrowDown className="text-green-600" size={24} strokeWidth={2.5} />
                <div className="bg-green-100 px-2 py-1 rounded text-xs font-semibold text-green-700">
                  Parent B Context
                </div>
              </div>

              {/* Children B */}
              <div className="flex gap-3">
                <div className="flex flex-col items-center space-y-2">
                  <div className="bg-gradient-to-r from-emerald-400 to-emerald-500 text-white px-5 py-3 rounded-lg shadow-lg border border-emerald-600">
                    <div className="font-semibold text-center text-sm">Child B1</div>
                  </div>
                  <ArrowUp className="text-emerald-600" size={20} strokeWidth={2.5} />
                  <div className="bg-emerald-100 px-2 py-1 rounded text-xs font-semibold text-emerald-700">
                    B1 Context
                  </div>
                </div>
                
                <div className="flex flex-col items-center space-y-2">
                  <div className="bg-gradient-to-r from-emerald-400 to-emerald-500 text-white px-5 py-3 rounded-lg shadow-lg border border-emerald-600">
                    <div className="font-semibold text-center text-sm">Child B2</div>
                  </div>
                  <ArrowUp className="text-emerald-600" size={20} strokeWidth={2.5} />
                  <div className="bg-emerald-100 px-2 py-1 rounded text-xs font-semibold text-emerald-700">
                    B2 Context
                  </div>
                </div>

                <div className="flex flex-col items-center space-y-2">
                  <div className="bg-gradient-to-r from-emerald-400 to-emerald-500 text-white px-5 py-3 rounded-lg shadow-lg border border-emerald-600">
                    <div className="font-semibold text-center text-sm">Child B3</div>
                  </div>
                  <ArrowUp className="text-emerald-600" size={20} strokeWidth={2.5} />
                  <div className="bg-emerald-100 px-2 py-1 rounded text-xs font-semibold text-emerald-700">
                    B3 Context
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 bg-green-200 px-4 py-2 rounded-lg border-2 border-green-400">
                <Merge className="text-green-700" size={20} />
                <span className="text-sm font-bold text-green-800">Merge: B1 + B2 + B3</span>
              </div>

              <ArrowUp className="text-green-600 animate-pulse" size={28} strokeWidth={3} />
            </div>

            {/* Parent C */}
            <div className="flex flex-col items-center space-y-4">
              <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white px-8 py-4 rounded-xl shadow-xl border-2 border-orange-700">
                <div className="text-xl font-bold text-center">Parent C</div>
              </div>
              
              <div className="flex flex-col items-center">
                <ArrowDown className="text-orange-600" size={24} strokeWidth={2.5} />
                <div className="bg-orange-100 px-2 py-1 rounded text-xs font-semibold text-orange-700">
                  Parent C Context
                </div>
              </div>

              {/* Children C */}
              <div className="flex gap-4">
                <div className="flex flex-col items-center space-y-2">
                  <div className="bg-gradient-to-r from-amber-400 to-amber-500 text-white px-6 py-3 rounded-lg shadow-lg border border-amber-600">
                    <div className="font-semibold text-center">Child C1</div>
                  </div>
                  <ArrowUp className="text-amber-600" size={20} strokeWidth={2.5} />
                  <div className="bg-amber-100 px-2 py-1 rounded text-xs font-semibold text-amber-700">
                    C1 Context
                  </div>
                </div>
                
                <div className="flex flex-col items-center space-y-2">
                  <div className="bg-gradient-to-r from-amber-400 to-amber-500 text-white px-6 py-3 rounded-lg shadow-lg border border-amber-600">
                    <div className="font-semibold text-center">Child C2</div>
                  </div>
                  <ArrowUp className="text-amber-600" size={20} strokeWidth={2.5} />
                  <div className="bg-amber-100 px-2 py-1 rounded text-xs font-semibold text-amber-700">
                    C2 Context
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 bg-orange-200 px-4 py-2 rounded-lg border-2 border-orange-400">
                <Merge className="text-orange-700" size={20} />
                <span className="text-sm font-bold text-orange-800">Merge: C1 + C2</span>
              </div>

              <ArrowUp className="text-orange-600 animate-pulse" size={28} strokeWidth={3} />
            </div>
          </div>

          {/* Final Root Merge */}
          <div className="flex items-center gap-3 bg-purple-200 px-8 py-4 rounded-xl border-4 border-purple-400 shadow-lg">
            <Merge className="text-purple-700" size={28} />
            <span className="text-lg font-bold text-purple-900">
              ROOT MERGE: Parent A + Parent B + Parent C
            </span>
          </div>

          {/* Final ROOT with complete context */}
          <div className="bg-gradient-to-r from-purple-600 to-purple-700 text-white px-12 py-6 rounded-2xl shadow-2xl border-4 border-purple-800">
            <div className="text-2xl font-bold text-center">ROOT</div>
            <div className="text-xs text-purple-200 text-center mt-1">Complete Aggregated Context</div>
          </div>
        </div>

        {/* Legend */}
        <div className="mt-12 bg-white p-6 rounded-xl shadow-lg border-2 border-gray-200">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Context Flow Legend</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <ArrowDown className="text-gray-600" size={20} />
              <span><strong>Downward:</strong> Context propagation (Parent → Child)</span>
            </div>
            <div className="flex items-center gap-2">
              <ArrowUp className="text-gray-600" size={20} />
              <span><strong>Upward:</strong> Context return (Child → Parent)</span>
            </div>
            <div className="flex items-center gap-2">
              <Merge className="text-gray-600" size={20} />
              <span><strong>Merge:</strong> Context aggregation at parent level</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-gradient-to-r from-purple-600 to-purple-700 rounded"></div>
              <span><strong>Purple:</strong> Root level</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-gradient-to-r from-blue-500 to-green-600 rounded"></div>
              <span><strong>Blue/Green/Orange:</strong> Parent levels</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-gradient-to-r from-cyan-400 to-amber-500 rounded"></div>
              <span><strong>Light colors:</strong> Child levels</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
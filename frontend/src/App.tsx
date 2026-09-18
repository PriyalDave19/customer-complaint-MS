import ComplaintForm from './components/ComplaintForm';
import AIAssistant from './components/AIAssistant';
import { Stethoscope } from 'lucide-react';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900">
      {/* Navbar (Optional, to make it look premium) */}
      <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center space-x-2 text-primary-700">
          <Stethoscope className="w-6 h-6" />
          <span className="text-xl font-bold tracking-tight">AIVOA</span>
          <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs font-semibold rounded ml-2">QMS</span>
        </div>
        <div className="flex items-center space-x-4">
          <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-700 font-bold text-sm border border-primary-200 shadow-sm">
            JD
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl mx-auto w-full">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8 h-[calc(100vh-8rem)]">
          <ComplaintForm />
          <AIAssistant />
        </div>
      </main>
    </div>
  );
}

export default App;

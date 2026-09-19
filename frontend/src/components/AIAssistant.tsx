import { useState, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { AppDispatch, RootState } from '../store';
import { extractComplaintData, refineComplaintData } from '../store/complaintSlice';
import { Sparkles, UploadCloud, FileText, Info, Bot, Send, AlertTriangle, CheckCircle, Target } from 'lucide-react';

const AIAssistant = () => {
  const [inputText, setInputText] = useState('');
  const [chatPrompt, setChatPrompt] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dispatch = useDispatch<AppDispatch>();
  const { status, extractionProgress, riskAssessment, error, formData } = useSelector((state: RootState) => state.complaint);

  const handleExtract = () => {
    if (!inputText.trim() && !selectedFile) return;
    dispatch(extractComplaintData({ text: inputText, file: selectedFile }));
  };

  const handleRefine = () => {
    if (!chatPrompt.trim()) return;
    dispatch(refineComplaintData({ current_data: formData, prompt: chatPrompt }));
    setChatPrompt('');
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col h-full lg:col-span-1">
      {/* Header */}
      <div className="p-5 border-b border-gray-100 flex justify-between items-center bg-gray-50/50 rounded-t-xl">
        <div className="flex items-center space-x-2 text-primary-600 font-semibold">
          <Sparkles className="w-5 h-5" />
          <span>AI Complaint Intake Assistant</span>
        </div>
        <span className="px-2 py-1 bg-primary-100 text-primary-700 text-[10px] font-bold rounded uppercase tracking-wide">
          Beta
        </span>
      </div>

      <div className="p-6 flex-1 overflow-y-auto space-y-6">
        {/* Upload Area */}
        <div 
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-gray-200 rounded-lg p-8 flex flex-col items-center justify-center text-center hover:border-primary-300 transition-colors cursor-pointer bg-gray-50/30"
        >
          <UploadCloud className="w-8 h-8 text-gray-400 mb-3" />
          <p className="text-sm font-medium text-gray-700">
            {selectedFile ? selectedFile.name : "Drag & drop complaint document here"}
          </p>
          <p className="text-sm text-primary-600 mt-1">
            {selectedFile ? "Click to change file" : "or click to browse"}
          </p>
          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                setSelectedFile(e.target.files[0]);
              }
            }}
          />
        </div>

        <div className="relative flex items-center py-2">
          <div className="flex-grow border-t border-gray-200"></div>
          <span className="flex-shrink-0 mx-4 text-gray-400 text-xs font-medium uppercase">and/or</span>
          <div className="flex-grow border-t border-gray-200"></div>
        </div>

        {/* Text Input Area */}
        <div>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 pt-3 pointer-events-none">
              <FileText className="h-5 w-5 text-gray-400" />
            </div>
       <textarea                                                 
              className="w-full pl-10 pr-3 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white shadow-sm text-sm"
              rows={4}
              placeholder="Paste Complaint Text / Email here..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />
          </div>
          <div className="mt-2 bg-green-50 border border-green-100 rounded-md p-3 flex items-start space-x-2">
            <Info className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
            <div className="text-xs text-green-700">
              <p className="font-semibold">Supported formats: PDF, DOCX, TXT, EML</p>
              <p>Max file size: 10MB</p>
            </div>
          </div>
        <button
            onClick={handleExtract}
            disabled={status === 'loading' || (!inputText.trim() && !selectedFile)}
            className="w-full mt-4 bg-primary-600 text-white rounded-lg py-2.5 text-sm font-semibold hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm flex items-center justify-center"
          >
            {status === 'loading' ? 'Extracting...' : 'Extract Details'}
          </button>
        </div>

        {/* Progress Bar */}
        {(status === 'loading' || status === 'succeeded') && (
          <div className="space-y-2 pt-2">
            <div className="flex justify-between text-xs font-bold text-gray-400 uppercase tracking-wider">
              <span>Extraction Progress</span>
              <span className="text-primary-600">{extractionProgress}%</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
              <div
                className="bg-primary-500 h-2.5 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${extractionProgress}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500">
              {status === 'loading' 
                ? 'Analyzing document content and extracting key details... Please wait.' 
                : 'Extraction complete. Form populated.'}
            </p>
          </div>
        )}

        {/* Error State */}
        {status === 'failed' && (
          <div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm border border-red-100">
            <p className="font-semibold">Extraction Failed</p>
            <p>{error}</p>
          </div>
        )}

        {/* Risk Assessment Panel (Bonus) */}
        {riskAssessment && (
          <div className="mt-6 border border-primary-100 rounded-lg overflow-hidden shadow-sm">
            <div className="bg-primary-50 px-4 py-3 border-b border-primary-100 flex items-center space-x-2">
              <Shield className="w-4 h-4 text-primary-600" />
              <h3 className="text-sm font-bold text-primary-900">AI Copilot Risk Assessment</h3>
            </div>
            <div className="p-4 bg-white space-y-4">
              <div>
                <span className="text-xs font-bold text-gray-500 uppercase">Risk Classification</span>
                <div className="mt-1 flex items-center space-x-2">
                  {riskAssessment.risk_class === 'Critical' ? <AlertTriangle className="w-4 h-4 text-red-500" /> :
                   riskAssessment.risk_class === 'Major' ? <AlertTriangle className="w-4 h-4 text-orange-500" /> :
                   <CheckCircle className="w-4 h-4 text-green-500" />}
                  <span className={`text-sm font-semibold ${
                    riskAssessment.risk_class === 'Critical' ? 'text-red-700' :
                    riskAssessment.risk_class === 'Major' ? 'text-orange-700' : 'text-green-700'
                  }`}>
                    {riskAssessment.risk_class || 'Unclassified'}
                  </span>
                </div>
              </div>
              
              <div className="bg-gray-50 p-3 rounded-md border border-gray-100">
                <div className="flex items-center space-x-2 mb-1">
                  <Target className="w-4 h-4 text-gray-400" />
                  <span className="text-xs font-bold text-gray-700">Potential Root Cause</span>
                </div>
                <p className="text-sm text-gray-600">{riskAssessment.root_cause_hypothesis || 'N/A'}</p>
              </div>

              <div className="bg-blue-50 p-3 rounded-md border border-blue-100">
                <div className="flex items-center space-x-2 mb-1">
                  <Info className="w-4 h-4 text-blue-400" />
                  <span className="text-xs font-bold text-blue-800">CAPA Recommendation</span>
                </div>
                <p className="text-sm text-blue-700">{riskAssessment.capa_recommendation || 'N/A'}</p>
              </div>
            </div>
          </div>
        )}

        {/* Chat / Assistant prompt */}
        {!riskAssessment && (
          <div className="bg-primary-50 border border-primary-100 rounded-lg p-4 flex items-start space-x-3">
            <div className="bg-primary-100 p-2 rounded-lg">
              <Bot className="w-5 h-5 text-primary-600" />
            </div>
            <div className="text-sm text-primary-800">
              <p>Upload a complaint document or paste text above.</p>
              <p className="mt-1 opacity-80">I will automatically extract the details, populate the form for you, and perform a risk assessment.</p>
            </div>
          </div>
        )}
      </div>

      {/* Chat Input area */}
      <div className="p-4 border-t border-gray-100 bg-white rounded-b-xl">
        <div className="relative">
          <input
            type="text"
            value={chatPrompt}
            onChange={(e) => setChatPrompt(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleRefine();
            }}
            placeholder="Ask me anything to update the form..."
            className="w-full pl-4 pr-12 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm shadow-sm"
          />
          <button 
            onClick={handleRefine}
            disabled={status === 'loading'}
            className="absolute right-2 top-2 p-1.5 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-center text-[10px] text-gray-400 mt-2">
          AI responses may contain errors. Please verify information.
        </p>
      </div>
    </div>
  );
};

// Add missing icon 
const Shield = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
  </svg>
);

export default AIAssistant;

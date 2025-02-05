import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Settings, Database, Activity, Brain, AlertTriangle } from 'lucide-react';
import Papa from 'papaparse';
import { Alert, AlertDescription } from '@/components/ui/alert';

const EnhancedDashboard = () => {
  const [activeUseCase, setActiveUseCase] = useState('drug-discovery');
  const [systemMetrics, setSystemMetrics] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [processingStatus, setProcessingStatus] = useState('idle');
  const [nodeStatus, setNodeStatus] = useState([]);

  // Enhanced use cases including new ones
  const useCases = [
    { id: 'drug-discovery', name: 'Drug Discovery', icon: Brain },
    { id: 'material-discovery', name: 'Material Discovery', icon: Database },
    { id: 'risk-assessment', name: 'Business Risk Assessment', icon: AlertTriangle },
    { id: 'quantum-simulation', name: 'Quantum Process Simulation', icon: Activity },
    { id: 'climate-modeling', name: 'Climate Pattern Analysis', icon: Settings },
  ];

  // Mock function to handle file processing
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      try {
        const fileContent = await window.fs.readFile(file.name, { encoding: 'utf8' });
        Papa.parse(fileContent, {
          complete: (results) => {
            setUploadedFiles(prev => [...prev, {
              name: file.name,
              data: results.data,
              status: 'processed'
            }]);
          },
          header: true,
          dynamicTyping: true,
          skipEmptyLines: true
        });
      } catch (error) {
        console.error('Error reading file:', error);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Kaleidoscope AI Dashboard</h1>
        <p className="text-gray-600">Advanced Analysis and Visualization System</p>
      </div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-12 gap-6">
        {/* Sidebar - Use Cases */}
        <div className="col-span-3 bg-white rounded-lg p-4 shadow">
          <h2 className="text-xl font-semibold mb-4">Use Cases</h2>
          <div className="space-y-2">
            {useCases.map((useCase) => (
              <button
                key={useCase.id}
                onClick={() => setActiveUseCase(useCase.id)}
                className={`w-full flex items-center p-2 rounded ${
                  activeUseCase === useCase.id 
                    ? 'bg-blue-100 text-blue-600' 
                    : 'hover:bg-gray-100'
                }`}
              >
                <useCase.icon className="w-5 h-5 mr-2" />
                <span>{useCase.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Main Content Area */}
        <div className="col-span-9 space-y-6">
          {/* System Metrics */}
          <div className="bg-white rounded-lg p-4 shadow">
            <h2 className="text-xl font-semibold mb-4">Real-time System Metrics</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={systemMetrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="energy" stroke="#8884d8" />
                  <Line type="monotone" dataKey="knowledge" stroke="#82ca9d" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* File Upload and Processing */}
          <div className="bg-white rounded-lg p-4 shadow">
            <h2 className="text-xl font-semibold mb-4">Data Processing</h2>
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <input
                  type="file"
                  onChange={handleFileUpload}
                  className="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-full file:border-0
                    file:text-sm file:font-semibold
                    file:bg-blue-50 file:text-blue-700
                    hover:file:bg-blue-100"
                />
                <button
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  onClick={() => setProcessingStatus('processing')}
                >
                  Process Data
                </button>
              </div>

              {/* Processing Status */}
              {processingStatus === 'processing' && (
                <Alert>
                  <AlertDescription>
                    Processing data... Please wait.
                  </AlertDescription>
                </Alert>
              )}

              {/* Uploaded Files List */}
              <div className="mt-4">
                <h3 className="text-lg font-semibold mb-2">Uploaded Files</h3>
                <div className="space-y-2">
                  {uploadedFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <span>{file.name}</span>
                      <span className="text-green-600">{file.status}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Node Status Grid */}
          <div className="bg-white rounded-lg p-4 shadow">
            <h2 className="text-xl font-semibold mb-4">Node Status</h2>
            <div className="grid grid-cols-3 gap-4">
              {nodeStatus.map((node, index) => (
                <div key={index} className="p-4 border rounded">
                  <h3 className="font-semibold">{node.id}</h3>
                  <div className="text-sm text-gray-600">
                    <p>Energy: {node.energy}%</p>
                    <p>Knowledge: {node.knowledge}%</p>
                    <p>Status: {node.status}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedDashboard;